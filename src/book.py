import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81"

def download_image(url, file_name):
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
    else:
        print(f'Failed to download image. Status code: {response.status_code}')

class Chapter:
    def __init__(self, number, title, text):
        self.number = number
        self.title = title
        self.text = text

    def print(self):
        print(self.title, '\n\n', self.text)

    def get_filename(self):
        return f'{self.number}.xhtml'

class Book(ABC):
    def __init__(self, url):
        self.chapters = []
        self.url = url
        res = requests.get(url)
        self.soup = BeautifulSoup(res.content, 'html.parser')

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_author(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_cover(self):
        pass

    @abstractmethod
    def get_chapters(self):
        pass

    def debug_print(self):
        with open('debug.html', 'w') as f:
            for chapter in self.chapters:
                f.write(chapter.title + '\n' + BeautifulSoup(chapter.text, 'html.parser').prettify() + '\n' * 4)
