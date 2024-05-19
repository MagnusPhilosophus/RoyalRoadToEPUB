import re
from book import *
from playwright.sync_api import Page, expect, sync_playwright

def remove_tags(soup, tags):
    for tag in tags:
        for element in soup.find_all(tag):
            element.unwrap()

class LightNovelWorldBook(Book):
    def __init__(self, url):
        self.chapters = []
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch()
        self.context = self.browser.new_context(user_agent=user_agent)
        self.page = self.context.new_page()
        self.page.goto(url)
        self.soup = BeautifulSoup(self.page.content(), 'html.parser')

    def get_title(self):
        return self.soup.find('h1', class_='novel-title').get_text().strip()

    def get_author(self):
        return self.soup.find('span', {'itemprop' : 'author'}).get_text().strip()

    def get_description(self):
        def delete_last_lines(text):
            lines = text.split('\n')
            lines = lines[:-3]
            updated_text = '\n'.join(lines)
            return updated_text
        return delete_last_lines(self.soup.find('div', class_='content').get_text()).strip()

    def get_cover(self):
        book_cover_url = self.soup.find('img', class_='ls-is-cached lazyloaded').get('src')
        book_cover_path = 'cover.jpg'
        download_image(book_cover_url, book_cover_path)
        return book_cover_path

    def get_chapters(self):
        self.page.get_by_role("link", name="Read Chapter").click()
        self.page.wait_for_timeout(500)
        soup = BeautifulSoup(self.page.content(), 'html.parser')

        chapter_counter = 0
        while True:
            chapter_counter += 1
            chapter_title = soup.find('span', class_='chapter-title').get_text().strip()
            chapter_text_soup = soup.find('div', id='chapter-container')
            remove_tags(chapter_text_soup, ['div', 'iframe'])
            chapter_text = str(chapter_text_soup)
            print(f'Writing chapter_{chapter_counter}: "{chapter_title}"')
            self.chapters.append(Chapter(chapter_counter, chapter_title, chapter_text))

            button = soup.find('a', class_='button nextchap')
            if not button:
                break

            self.page.close()
            self.page = self.context.new_page()
            self.page.goto(f"https://www.lightnovelworld.com{button.get('href')}")
            self.page.wait_for_timeout(1700)
            soup = BeautifulSoup(self.page.content(), 'html.parser')

    def __del__(self):
        self.context.close()
        self.browser.close()
        self.p.stop()
