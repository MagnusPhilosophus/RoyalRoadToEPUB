from book import *
from urllib.parse import urljoin

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
