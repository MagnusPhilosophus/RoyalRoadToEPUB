from playwright.sync_api import Page, expect, sync_playwright
import random
import time
import requests
import re
import os 
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ebooklib import epub
from abc import ABC, abstractmethod

def download_image(url, file_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
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
        return f'chapter_{self.number}: "{self.title}".xhtml'

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

class LightNovelWorldBook(Book):
    def __init__(self, url):
        self.chapters = []
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False, slow_mo=250)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(url)
        self.soup = BeautifulSoup(self.page.content(), 'html.parser')

    def get_title(self):
        return self.soup.find('h1', class_='novel-title').get_text()

    def get_author(self):
        return self.soup.find('span', {'itemprop' : 'author'}).get_text()

    def get_description(self):
        def delete_last_lines(text):
            lines = text.split('\n')
            lines = lines[:-3]
            updated_text = '\n'.join(lines)
            return updated_text
        return delete_last_lines(self.soup.find('div', class_='content').get_text())

    def get_cover(self):
        book_cover_url = self.soup.find('img', class_='ls-is-cached lazyloaded').get('src')
        book_cover_path = 'cover.jpg'
        download_image(book_cover_url, book_cover_path)
        return book_cover_path

    def get_chapters(self):
        url = self.soup.find('a', id='readchapterbtn').get('href')
        self.page.goto(f'https://www.lightnovelworld.com{url}')
        self.soup = BeautifulSoup(self.page.content(), 'html.parser')

        chapter_counter = 0
        is_next_chapter_available = True
        while is_next_chapter_available:
            chapter_counter += 1
            if chapter_counter % 50 == 0:
                time.sleep(60)
            chapter_title = self.soup.find('span', class_='chapter-title').get_text()
            chapter_text = str(self.soup.find('div', id='chapter-container'))
            print(f'Writing chapter_{chapter_counter}: "{chapter_title}"')
            self.chapters.append(Chapter(chapter_counter, chapter_title, chapter_text))
            button = self.soup.find('a', class_='button nextchap')
            if 'isDisabled' in button.get('class', []):
                print("last button")
                is_next_chapter_available = False
                break
            time.sleep(2)
            try:
                print(button.get('href'))
                self.page.goto(f"https://www.lightnovelworld.com{button.get('href')}")
            except Exception as e:
                print(f"Exception occurred: {e}")
            #page.frame_locator("iframe[title=\"Widget containing a Cloudflare security challenge\"]").get_by_label("Verify you are human").check()
            #self.page.wait_for_selector('span.chapter-title', timeout=random.uniform(10, 50) * 1000)
            self.soup = BeautifulSoup(self.page.content(), 'html.parser')

    def __del__(self):
        self.context.close()
        self.browser.close()
        self.p.stop()

class RoyalRoadBook(Book):
    def get_title(self):
        return self.soup.find('h1', class_='font-white').get_text()

    def get_author(self):
        return self.soup.find('a', class_='font-white').get_text()

    def get_description(self):
        return self.soup.find('div', class_='description').get_text()

    def get_cover(self):
        book_cover_url = self.soup.find('img', class_='thumbnail').get('src')
        book_cover_path = 'cover.jpg'
        download_image(book_cover_url, book_cover_path)
        return book_cover_path

    def get_chapters(self):
        tr = self.soup.find('tr', class_='chapter-row')
        link = tr.find('a', href=True)['href']
        next_url = urljoin(self.url, link)
        response = requests.get(next_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        chapter_counter = 0
        is_next_chapter_available = True

        while is_next_chapter_available:
            chapter_counter += 1
            chapter_title = soup.find('h1', class_='font-white break-word').get_text()
            chapter_text = str(soup.find('div', class_='chapter-content'))
            print(f'Writing chapter_{chapter_counter}: "{chapter_title}"')
            self.chapters.append(Chapter(chapter_counter, chapter_title, chapter_text))

            links = soup.find_all('a', {'disabled' : False}, class_='btn btn-primary col-xs-12')
            links = list(filter(lambda l: 'Next' in l.get_text(), links))

            if len(links) == 0:
                is_next_chapter_available = False
                break

            link = links[0]
            next_url = urljoin(self.url, link.get('href'))
            response = requests.get(next_url)
            soup = BeautifulSoup(response.content, 'html.parser')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No arguments provided")
        exit()
    url = sys.argv[1]
    book = LightNovelWorldBook(url)
    #print(book.get_title())
    #print(book.get_author())
    #print(book.get_description())
    #book.get_cover()
    book.get_chapters()
    del book
    '''
    book = RoyalRoadBook(url)

    epub_book = epub.EpubBook()
    epub_book.set_title(book.get_title())
    epub_book.add_author(book.get_author())
    epub_book.add_metadata('DC', 'description', book.get_description())
    cover_path = book.get_cover()
    epub_book.set_cover('cover.jpg', open(cover_path, 'rb').read())
    os.remove(cover_path)
    epub_book.set_language('en')
    book.get_chapters()

    epub_chapters = []
    for chapter in book.chapters:
        epub_chapter = epub.EpubHtml(title=chapter.title,
                                     file_name=chapter.get_filename(),
                                     lang='en')
        epub_chapter.set_content(chapter.text)
        epub_chapters.append(epub_chapter)
        epub_book.add_item(epub_chapter)

    style = 'body { font-family: Times, Times New Roman, serif; }'

    nav_css = epub.EpubItem(uid="style_nav",
                            file_name="style/nav.css",
                            media_type="text/css",
                            content=style)
    epub_book.add_item(nav_css)

    epub_book.toc = ([epub.Link(chapter.get_filename(), chapter.title, chapter.title) for chapter in book.chapters])

    epub_book.spine = ['nav', *epub_chapters]
    epub_book.add_item(epub.EpubNcx())
    epub_book.add_item(epub.EpubNav())

    epub.write_epub(f'{book.get_title()}.epub', epub_book)
    '''
#url = 'https://www.royalroad.com/fiction/36049/the-primal-hunter'
#url = 'https://www.royalroad.com/fiction/81581/amber-the-cursed-berserker'
