import requests
import re
import os 
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

chapters_dir = 'chapters'
os.makedirs(chapters_dir, exist_ok=True)

#url = 'https://www.royalroad.com/fiction/36049/the-primal-hunter'
#url = 'https://www.royalroad.com/fiction/81581/amber-the-cursed-berserker'
url = 'https://www.royalroad.com/fiction/33844/the-runesmith'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

book_title = soup.find('h1', class_='font-white').get_text()
book_author = soup.find('a', class_='font-white').get_text()
book_description = soup.find('div', class_='description').get_text()
book_cover_url = soup.find('img', class_='thumbnail').get('src')
book_cover_path = os.path.join(chapters_dir, 'image.jpg')
download_image(book_cover_url, book_cover_path)

book = epub.EpubBook()

book.set_title(book_title)
book.set_language('en')
book.add_author(book_author)
book.add_metadata('DC', 'description', book_description)
book.set_cover('image.jpg', open(book_cover_path, 'rb').read())

tr = soup.find('tr', class_='chapter-row')
link = tr.find('a', href=True)['href']
next_url = urljoin(url, link)
response = requests.get(next_url)
soup = BeautifulSoup(response.content, 'html.parser')

chapters = []
chapter_counter = 0
is_next_chapter_available = True

while is_next_chapter_available:# and chapter_counter < 5:
    chapter_counter += 1
    chapter_title = soup.find('h1', class_='font-white break-word').get_text()
    chapter_text = str(soup.find('div', class_='chapter-content'))
    chapters.append(Chapter(chapter_counter, chapter_title, chapter_text))

    with open(os.path.join(chapters_dir, f'chapter_{chapter_counter}: "{chapter_title}".html'), 'w') as f:
        print(f'Writing chapter "{chapter_title}"')
        f.write(chapter_text)

    links = soup.find_all('a', {'disabled' : False}, class_='btn btn-primary col-xs-12')
    links = list(filter(lambda l: 'Next' in l.get_text(), links))

    if len(links) == 0:
        is_next_chapter_available = False
        break

    link = links[0]
    next_url = urljoin(url, link.get('href'))
    response = requests.get(next_url)
    soup = BeautifulSoup(response.content, 'html.parser')


epub_chapters = []
for chapter in chapters:
    epub_chapter = epub.EpubHtml(title=chapter.title,
                                 file_name=chapter.get_filename(),
                                 lang='en')
    epub_chapter.set_content(chapter.text)
    epub_chapters.append(epub_chapter)
    book.add_item(epub_chapter)

style = 'body { font-family: Times, Times New Roman, serif; }'

nav_css = epub.EpubItem(uid="style_nav",
                        file_name="style/nav.css",
                        media_type="text/css",
                        content=style)
book.add_item(nav_css)

#book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'), ( epub.Section('Languages'), (*epub_chapters)))

book.toc = ([epub.Link(chapter.get_filename(), chapter.title, chapter.title) for chapter in chapters])

book.spine = ['nav', *epub_chapters]
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

epub.write_epub(f'{book_title}.epub', book)

