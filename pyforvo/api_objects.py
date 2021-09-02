import requests
import subprocess
import tempfile


class Word(object):
    def __init__(self, id, word, original, added, hits, username, sex, country, code, language, mp3_path, ogg_path,
                 rate, votes, positive_votes):
        self.id = id
        self.word = word
        self.original = original
        self.added = added
        self.hits = hits
        self.username = username
        self.sex = sex
        self.country = country
        self.code = code
        self.language = language
        self.mp3_path = mp3_path
        self.ogg_path = ogg_path
        self.rate = rate
        self.votes = votes
        self.positive_votes = positive_votes

    def download(self, path=None, fmt='mp3'):

        if fmt == 'ogg':
            response = requests.get(self.ogg_path)
        else:
            response = requests.get(self.mp3_path)

        if path is None:
            path = f'{self.word}_{self.username}.{fmt}'

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def play(self, fmt='mp3'):
        # TODO: implement for multiple OSes; don't download if already present
        with tempfile.TemporaryDirectory() as temp_dir:
            path = f'{temp_dir}/{self.word}_{self.username}.{fmt}'
            self.download(path)
            subprocess.Popen(['mplayer', path]).wait()


class Language(object):
    def __init__(self, code, en, language):
        self.code = code
        self.en = en
        self.language = language
