import requests
from pyforvo.api_objects import Word, Language


class Forvo(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = f'https://apifree.forvo.com/key/{api_key}/format/json/action'

    def get_pronunciation(self, word, language=None):
        url = f'{self.base_url}/standard-pronunciation/word/{word}/'
        if language:
            url = f'{url}/language/{language}'

        item = self._get(url)[0]
        return self._word(item)

    def get_pronunciations(self, word, language=None, country=None, username=None, sex=None, rate=None, order=None,
                           limit=None, group=None):

        url = f'{self.base_url}/word-pronunciations/word/{word}'
        if language:
            url = f'{url}/language/{language}'
        if country:
            url = f'{url}/country/{country}'
        if username:
            url = f'{url}/username/{username}'
        if sex:
            url = f'{url}/sex/{sex}'
        if rate:
            url = f'{url}/rate/{rate}'
        if order:
            url = f'{url}/order/{order}'
        if limit:
            url = f'{url}/limit/{limit}'
        if group:
            url = f'{url}/group-in-language/{group}'

        words = []
        items = self._get(url)
        for item in items:
            words.append(self._word(item))
        return words

    def get_languages(self, language=None, order=None, min_pronunciations=None):
        url = f'{self.base_url}/language-list'
        if language:
            url = f'{url}/language/{language}'
        if order:
            url = f'{url}/order/{order}'
        if min_pronunciations:
            url = f'{url}/min-pronunciations/{min_pronunciations}'

        langs = []
        items = self._get(url)
        for item in items:
            langs.append(self._language(item))
        return langs

    def get_language_code(self, language):
        langs = self.get_languages()
        for lang in langs:
            if lang.language == language:
                return lang.code

    def _get(self, url):
        response = requests.get(url)
        # print(response.status_code, response.reason, response.json())
        rjson = response.json()
        if rjson.get('items'):
            return rjson.get('items')

    @staticmethod
    def _word(item):
        word = Word(id=item.get('id'),
                    word=item.get('word'),
                    original=item.get('original'),
                    added=item.get('addtime'),
                    hits=item.get('hits'),
                    username=item.get('username'),
                    sex=item.get('sex'),
                    country=item.get('country'),
                    code=item.get('code'),
                    language=item.get('langname'),
                    mp3_path=item.get('pathmp3'),
                    ogg_path=item.get('pathogg'),
                    rate=item.get('rate'),
                    votes=item.get('num_votes'),
                    positive_votes=item.get('num_positive_votes'))
        return word

    @staticmethod
    def _language(item):
        lang = Language(code=item.get('code'),
                        en=item.get('en'),
                        language=item.get('language'))
        return lang
