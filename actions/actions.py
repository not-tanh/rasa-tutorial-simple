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


# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

google_url = 'https://www.google.com.vn/search'
news_url = 'https://vnexpress.net/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/64.0.3282.186 '
                  'Safari/537.36'
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

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        condition, degree = self.get_weather()
        dispatcher.utter_message(template='utter_weather', condition=condition, degree=degree)
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
        location_stamp = top_story_article.find('span', {'class': 'location-stamp'}).text.strip()
        # Delete location stamp in description
        desc = desc.replace(location_stamp, '', 1).strip()
        return '%s\n%s' % (title, desc)

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        news = self.get_news()
        dispatcher.utter_message(text=news)
