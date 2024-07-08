import os
import sys
from ebooklib import epub
from light_novel_world import LightNovelWorldBook
from royal_road import RoyalRoadBook
from novel_next import NovelNextBook

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
    elif 'novelnext' in url:
        book = NovelNextBook(url)
    else:
        print(f'No support for {url} yet')

    epub_book = epub.EpubBook()

    epub_book.set_identifier(book.get_title().lower().replace(' ', '-'))
    epub_book.set_title(book.get_title())
    epub_book.set_language('en')
    epub_book.add_author(book.get_author())
    epub_book.add_metadata('DC', 'description', book.get_description())
    cover_path = book.get_cover()
    # epub_book.set_cover("cover.jpg", open(cover_path, 'rb').read())
    # Create a cover page
    cover_html = epub.EpubHtml(title='Cover', file_name='cover.xhtml', lang='en')
    cover_html.content = f'''
<html>
<head>
    <title>Cover</title>
    <style>
        @page {{ margin: 0; }}
        body {{ margin: 0; text-align: center; }}
        img {{ width: 100%; height: auto; }}
    </style>
</head>
<body>
    <img src="cover.jpg" alt="Cover Image"/>
</body>
</html>'''
    epub_book.add_item(cover_html)

    book.get_chapters()

    epub_chapters = []
    for chapter in book.chapters:
        epub_chapter = epub.EpubHtml(title=chapter.title,
                                     file_name=chapter.get_filename(),
                                     lang='en')
        epub_chapter.set_content(chapter.text)
        epub_chapters.append(epub_chapter)
        epub_book.add_item(epub_chapter)

    style = '''
@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}
h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;
}
ol {
        list-style-type: none;
}
ol > li:first-child {
        margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}
'''

    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    epub_book.add_item(nav_css)

    epub_book.toc = ([epub.Link(chapter.get_filename(), chapter.title, chapter.title) for chapter in book.chapters])

    epub_book.spine = ['cover', 'nav'] + epub_chapters
    epub_book.add_item(epub.EpubNcx())
    epub_book.add_item(epub.EpubNav())

    epub.write_epub(f'{book.get_title()}.epub', epub_book)
    os.remove(cover_path)
    book.debug_print()
