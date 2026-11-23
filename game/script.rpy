## Entry point. "Start" on the main menu opens the Library.
## The Library loop calls chapters, marks them finished and returns to the shelf.

label start:
    jump library_loop

label library_loop:
    $ _lib_result = renpy.call_screen("library")

    if _lib_result[0] == "quit":
        return

    $ _lib_book_id = _lib_result[1]
    jump book_loop

label book_loop:
    $ _lib_book = vn_book(_lib_book_id)
    $ _lib_result = renpy.call_screen("book_detail", book=_lib_book)

    if _lib_result[0] == "back":
        jump library_loop

    $ _lib_chapter_id = _lib_result[2]
    $ _lib_label = _lib_book.chapter(_lib_chapter_id).label
    $ _lib_book = None

    window hide
    scene black with dissolve
    call expression _lib_label from _lib_call_chapter
    $ vn_complete(_lib_book_id, _lib_chapter_id)

    scene black with dissolve
    jump book_loop
