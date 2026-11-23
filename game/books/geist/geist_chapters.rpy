## geist chapters - PLACEHOLDER content.
## Replace each label's body with the converted script. Keep the label
## names in sync with library_books.rpy and end every chapter with `return`.

label geist_ch1:
    scene bg placeholder with dissolve
    show geist with dissolve
    "[[Placeholder] Geist, chapter 1."
    hide geist
    return

label geist_ch2:
    scene bg placeholder with dissolve
    show geist with dissolve
    "[[Placeholder] Geist, chapter 2."
    "This chapter shows how a branch works."
    menu:
        "Take path A":
            $ vn_flag("geist_path_a")
            "Path A chosen. Chapter 3a will open in the Library."
        "Take path B":
            $ vn_flag("geist_path_b")
            "Path B chosen. Chapter 3b will open in the Library."
    hide geist
    return

label geist_ch3a:
    scene bg placeholder with dissolve
    show geist with dissolve
    "[[Placeholder] Geist, chapter 3a."
    hide geist
    return

label geist_ch3b:
    scene bg placeholder with dissolve
    show geist with dissolve
    "[[Placeholder] Geist, chapter 3b."
    hide geist
    return

label geist_ch4:
    scene bg placeholder with dissolve
    show geist with dissolve
    "[[Placeholder] Geist, chapter 4."
    hide geist
    return

label geist_ch5x:
    scene bg placeholder with dissolve
    show geist with dissolve
    "[[Placeholder] Geist, chapter 5x."
    $ vn_ending("geist_secret")
    "You reached a hidden ending."
    hide geist
    return
