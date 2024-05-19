import os
import sys
from ebooklib import epub
from light_novel_world import LightNovelWorldBook
from royal_road import RoyalRoadBook

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No arguments provided")
        exit()
    url = sys.argv[1]
    book = None
    if 'royalroad' in url:
        book = RoyalRoadBook(url)
    elif 'lightnovelworld' in url:
        book = LightNovelWorldBook(url)
    else:
        print(f'No support for {url} yet')

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
    #book.debug_print()
