# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from bs4 import BeautifulSoup

google_url = 'https://www.google.com.vn/search'
news_url = 'https://vnexpress.net/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/64.0.3282.186 '
                  'Safari/537.36'
}
news_type_to_path = {
    'thế giới': 'the-gioi',
    'kinh doanh': 'kinh-doanh',
    'giải trí': 'giai-tri',
    'thể thao': 'the-thao',
    'pháp luật': 'phap-luat',
    'giáo dục': 'giao-duc',
    'sức khỏe': 'suc-khoe',
    'đời sống': 'doi-song',
    'du lịch': 'du-lich',
    'khoa học': 'khoa-hoc'
}


class ActionGetWeatherInfo(Action):
    def name(self) -> Text:
        return 'action_get_weather_info'

    @staticmethod
    def get_weather():
        # Returns weather condition and degree
        r = requests.get(google_url,
                         params={'q': 'thời tiết ở Hà Nội', 'cr': 'countryVN', 'lr': 'lang_vi', 'hl': 'vi'},
                         headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        weather_box = soup.find('div', {'id': 'wob_dcp'})
        if weather_box:
            degree = soup.find('span', {'id': 'wob_tm'})
            condition = weather_box.text
            return condition.lower(), degree.text.strip()
        return '', ''

    @staticmethod
    def get_weather_in_location(locations):
        # Returns list of weather conditions, degrees and location
        results = []
        if type(locations) is str:
            locations = [locations]
        locations = set(locations)
        for location in locations:
            r = requests.get(google_url,
                             params={'q': 'thời tiết ở %s' % location, 'cr': 'countryVN', 'lr': 'lang_vi', 'hl': 'vi'},
                             headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            weather_box = soup.find('div', {'id': 'wob_dcp'})
            if weather_box:
                degree = soup.find('span', {'id': 'wob_tm'})
                condition = weather_box.text
                results.append((condition.lower(), degree.text.strip(), location))
        return results

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        locations = tracker.get_slot('location')
        results = self.get_weather_in_location(locations)
        if results:
            for condition, degree, location in results:

                dispatcher.utter_message(template='utter_weather',
                                         condition=condition, degree=degree, location=location)
        else:
            dispatcher.utter_message(text='Xin lỗi bạn, mình không tìm thấy thông tin')
        # This also works
        # dispatcher.utter_message(text="Hôm nay {condition}, nhiệt độ hiện tại là {degree} độ bạn nhé!")


class ActionGetNews(Action):
    def name(self) -> Text:
        return 'action_get_news'

    @staticmethod
    def get_news():
        # Returns top story in vnexpress
        r = requests.get(news_url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        top_story_article = soup.find('article', {'class': 'article-topstory'})
        title = top_story_article.find('h3', {'class': 'title-news'}).text.strip()
        desc = top_story_article.find('p', {'class': 'description'}).text
        location_stamp = top_story_article.find('span', {'class': 'location-stamp'})
        location_stamp = location_stamp.text.strip() if location_stamp else ''
        # Delete location stamp in description (if any)
        desc = desc.replace(location_stamp, '', 1).strip()
        return '%s\n%s' % (title, desc)

    @staticmethod
    def get_news_by_type(news_types):
        # Returns top story in vnexpress
        results = []
        if type(news_types) is str:
            news_types = [news_types]
        news_types = set(news_types)
        for news_type in news_types:
            news_path = news_type_to_path.get(news_type, '')
            if not news_path:
                continue
            r = requests.get(news_url + news_path, headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            top_story_article = soup.find('article', {'class': 'article-topstory'})
            title = top_story_article.find('h3', {'class': 'title-news'}).text.strip()
            desc = top_story_article.find('p', {'class': 'description'}).text
            location_stamp = top_story_article.find('span', {'class': 'location-stamp'})
            location_stamp = location_stamp.text.strip() if location_stamp else ''
            # Delete location stamp in description (if any)
            desc = desc.replace(location_stamp, '', 1).strip()
            results.append('Tin %s:\n%s\n%s' % (news_type.lower(), title, desc))
        return results

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        news_types = tracker.get_slot('news_type')
        news_list = self.get_news_by_type(news_types)
        if news_list:
            for news in news_list:
                dispatcher.utter_message(text=news)
        else:
            dispatcher.utter_message(text='Xin lỗi bạn, mình không tìm thấy thông tin')
