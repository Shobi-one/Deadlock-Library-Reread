## The Library UI: the bookshelf and the per-book chapter select.

define lib_gold = "#c9a86a"
define lib_ink = "#f3e9d2"
define lib_dim = "#8c8577"

style lib_title is text:
    font gui.name_text_font
    size 72
    color lib_gold
    kerning 6

style lib_heading is text:
    size 40
    color lib_ink

style lib_body is text:
    size 26
    color lib_ink

style lib_small is text:
    size 22
    color lib_dim

style lib_button is button:
    padding (24, 12)
    background Solid("#00000066")
    hover_background Solid("#c9a86a33")
    insensitive_background Solid("#00000033")

style lib_button_text is text:
    size 28
    color lib_ink
    hover_color lib_gold
    insensitive_color "#5c574d"


## ------------------------------------------------------------------
## Bookshelf
## ------------------------------------------------------------------

screen library():
    tag menu
    add vn_bg("images/library/bg_library.png", "The Library")
    add Solid("#000000aa")

    vbox:
        xalign 0.5
        ypos 70
        spacing 8
        text "THE LIBRARY" style "lib_title" xalign 0.5
        text "Stories from the Cursed Apple" style "lib_small" xalign 0.5

    hbox:
        xalign 0.5
        yalign 0.58
        spacing 50

        for book in VN_BOOKS:
            $ done, total = book.progress()
            vbox:
                spacing 14
                xsize 360

                button:
                    padding (0, 0)
                    background None
                    hover_background None
                    hover_foreground Solid("#c9a86a22")
                    action Return(("book", book.id))
                    add book.cover()

                text book.title style "lib_body" xalign 0.5 text_align 0.5
                text "[book.hero]  ·  [done]/[total] chapters" style "lib_small" xalign 0.5

    hbox:
        xalign 0.5
        yalign 0.97
        spacing 30
        textbutton "Main Menu" style "lib_button" action Return(("quit",))
        textbutton "Reset progress" style "lib_button":
            action Confirm("Forget all finished chapters, choices and endings?", Function(vn_reset_progress))


## ------------------------------------------------------------------
## One book: cover, summary, chapter list
## ------------------------------------------------------------------

screen book_detail(book):
    tag menu
    add vn_bg("images/books/%s/bg_menu.png" % book.id, book.title)
    add Solid("#000000bb")

    hbox:
        xalign 0.5
        yalign 0.45
        spacing 80

        vbox:
            spacing 20
            add book.cover()

        vbox:
            spacing 18
            xsize 900

            text book.title style "lib_title" size 56
            text book.hero style "lib_heading" color book.accent
            text book.blurb style "lib_body"

            null height 20

            viewport:
                ysize 480
                mousewheel True
                scrollbars "vertical"

                vbox:
                    spacing 10
                    for ch in book.visible_chapters():
                        $ unlocked = book.is_unlocked(ch)
                        $ done = vn_is_complete(book.id, ch.id)
                        $ mark = "✓ " if done else ("" if unlocked else "Locked: ")
                        textbutton "[mark][ch.title]":
                            style "lib_button"
                            xsize 860
                            sensitive unlocked
                            action Return(("play", book.id, ch.id))
                        if not unlocked:
                            $ need = (" or " if ch.any_of else " and ").join(ch.requires)
                            if ch.flag:
                                text "    Make a different choice in chapter [need] to open this path." style "lib_small"
                            else:
                                text "    Finish chapter [need] first." style "lib_small"

    textbutton "← Back to the Library":
        style "lib_button"
        xalign 0.5
        yalign 0.97
        action Return(("back",))
