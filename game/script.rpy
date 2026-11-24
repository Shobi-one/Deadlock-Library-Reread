## Entry point. "Start" on the main menu opens the Library.
## The Library loop calls chapters, marks them finished and returns to the shelf.

label start:
    jump library_loop

label library_loop:
    $ lib_result = renpy.call_screen("library")

    if lib_result[0] == "quit":
        return

    $ lib_book_id = lib_result[1]
    jump book_loop

label book_loop:
    $ lib_book = vn_book(lib_book_id)
    $ lib_result = renpy.call_screen("book_detail", book=lib_book)

    if lib_result[0] == "back":
        jump library_loop

    $ lib_chapter_id = lib_result[2]
    $ lib_label = lib_book.chapter(lib_chapter_id).label
    $ lib_book = None

    window hide
    scene black with dissolve
    call expression lib_label from lib_call_chapter
    hide screen dl_reader
    $ vn_page_art = False
    $ quick_menu = True
    $ vn_complete(lib_book_id, lib_chapter_id)

    scene black with dissolve
    jump book_loop
