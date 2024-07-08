from book import *
from urllib.parse import urljoin

class NovelNextBook(Book):
    def get_title(self):
        return self.soup.find('h3', class_='title').get_text()

    def get_author(self):
        h3_tag = self.soup.find('h3', text='Author:')
        if h3_tag:
            author_tag = h3_tag.find_next_sibling('a')
            if author_tag:
                return author_tag.text.strip()

    def get_description(self):
        return self.soup.find('div', class_='desc-text').get_text()

    def get_cover(self):
        div_book = self.soup.find('div', class_='book')

        if div_book:
            img_tag = div_book.find('img')
            if img_tag:
                book_cover_url = img_tag.get('src')

        book_cover_path = 'cover.jpg'
        download_image(book_cover_url, book_cover_path)
        return book_cover_path

    def get_chapters(self):
        next_url = self.soup.find('a', class_='btn-read-now', href=True)['href']
        response = requests.get(next_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        chapter_counter = 0
        is_next_chapter_available = True

        while is_next_chapter_available:
            chapter_counter += 1
            chapter_title = soup.find('a', class_='chr-title').get_text().strip()
            chapter_text = str(soup.find('div', id='chr-content'))
            print(f'Writing chapter_{chapter_counter}: "{chapter_title}"')
            self.chapters.append(Chapter(chapter_counter, chapter_title, chapter_text))

            link = soup.find('a', id='next_chap_top')
            if link.get('href') == "":
                is_next_chapter_available = False
                break

            next_url = urljoin(self.url, link.get('href'))
            response = requests.get(next_url)
            soup = BeautifulSoup(response.content, 'html.parser')
