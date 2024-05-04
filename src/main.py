import requests
import re
import os 
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ebooklib import epub

def download_image(url, file_name):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)

class Chapter:
    def __init__(self, number, title, text):
        self.number = number
        self.title = title
        self.text = text

    def print(self):
        print(self.title, '\n\n', self.text)

    def get_filename(self):
        return f'chapter_{self.number}: "{self.title}".xhtml'

class Book:
    def __init__(self, url):
        self.chapters = []
        self.url = url
        res = requests.get(url)
        self.soup = BeautifulSoup(res.content, 'html.parser')

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

        while is_next_chapter_available and chapter_counter < 5:
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
    book = Book(url)

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
#url = 'https://www.royalroad.com/fiction/36049/the-primal-hunter'
#url = 'https://www.royalroad.com/fiction/81581/amber-the-cursed-berserker'
