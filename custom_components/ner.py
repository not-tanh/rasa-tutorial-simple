from rasa.nlu.components import Component
import underthesea


class NamedEntityRecognition(Component):
    """A pre-trained NER component"""
    name = "ner"
    provides = ["entities"]
    requires = []
    defaults = {}
    language_list = ["vi"]

    def __init__(self, component_config=None):
        super(NamedEntityRecognition, self).__init__(component_config)

    def train(self, training_data, cfg, **kwargs):
        """Not needed, because the the model is pretrained"""
        pass

    @staticmethod
    def convert_to_rasa(tokens):
        """Convert model output into the Rasa NLU compatible output format."""
        entities = []
        entity, value = '', ''
        for token in tokens:
            if token[3] != 'O':
                bi, ner = token[3].split('-')
                if bi == 'B':
                    if entity:
                        entities.append({"value": value, "confidence": 1, "entity": entity, "extractor": "ner"})
                    entity, value = ner, token[0]
                else:
                    value = value + ' ' + token[0]
            elif entity:
                entities.append({"value": value, "confidence": 1, "entity": entity, "extractor": "ner"})
                entity, value = '', ''
        if entity:
            entities.append({"value": value, "confidence": 1, "entity": entity, "extractor": "ner"})
        return entities

    def process(self, message, **kwargs):
        """Retrieve the text message, pass it to the classifier
            and append the prediction results to the message class."""
        if 'text' in message.data:
            tokens = underthesea.ner(message.data['text'])
            entities = self.convert_to_rasa(tokens)
            message.set("entities", entities, add_to_output=True)

    def persist(self, file_name, dir_name, **kwargs):
        """Pass because a pre-trained model is already persisted"""
        pass
