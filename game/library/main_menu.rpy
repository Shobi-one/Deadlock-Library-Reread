## Main menu in the style of Deadlock's Library (colours, fonts and art from
## the game files; see library_screens.rpy). screens.rpy's main_menu uses this.

transform dl_fade_in(delay=0.0):
    alpha 0.0 xoffset -24
    pause delay
    ease 0.6 alpha 1.0 xoffset 0

transform dl_cover_in:
    alpha 0.0 xoffset 60
    pause 0.3
    ease 0.9 alpha 1.0 xoffset 0

transform dl_cover_float:
    subpixel True
    rotate -4
    block:
        ease 3.5 yoffset -14
        ease 3.5 yoffset 0
        repeat

transform dl_glow_pulse:
    block:
        ease 3.5 alpha 0.35
        ease 3.5 alpha 0.18
        repeat

transform dl_menu_slide:
    on idle:
        ease 0.15 xoffset 0
    on hover:
        ease 0.15 xoffset 14

transform dl_menu_bar:
    on idle:
        ease 0.15 alpha 0.0 xsize 0
    on hover:
        ease 0.15 alpha 1.0 xsize 4

style dl_menu_button is button:
    background None
    padding (0, 6)

style dl_menu_button_text is dl_text:
    font DL_SANS
    size 36
    kerning 2
    color "#FFEFD7a6"
    hover_color dl_offwhite
    insensitive_color "#FFEFD740"

style dl_kicker is dl_text:
    font DL_SANS
    size 22
    kerning 8
    color dl_green

style dl_menu_title is dl_text:
    font DL_SERIF
    size 56

style dl_tagline is dl_text:
    size 26
    italic True
    color "#FFEFD7cc"

style dl_stats is dl_text:
    font DL_SANS
    size 18
    kerning 3
    color "#FFEFD799"

style dl_footer_note is dl_text:
    size 15
    color "#FFEFD766"

init python:

    def dl_menu_cover():
        """The cover shown on the main menu: the first book with real cover art."""
        for b in VN_BOOKS:
            path = "images/books/%s/cover.png" % b.id
            if renpy.loadable(path) and b.id == "geist":
                return b, path
        for b in VN_BOOKS:
            path = "images/books/%s/cover.png" % b.id
            if renpy.loadable(path):
                return b, path
        return None, None

screen dl_main_menu_item(label, action, delay):
    button:
        style "dl_menu_button"
        action action
        at dl_fade_in(delay)
        hbox:
            spacing 0
            at dl_menu_slide
            add Solid(dl_green, xysize=(4, 34)) yalign 0.5 at dl_menu_bar
            null width 14
            text label style "dl_menu_button_text" yalign 0.5

screen dl_main_menu():

    $ cover_book, cover = dl_menu_cover()

    # backdrop: Valve's black & white New York skyline
    add Solid("#000000")
    if dl_ui("library_bg"):
        add Transform(dl_ui("library_bg"), fit="cover", xysize=(1920, 1080), alpha=0.38)

    # featured cover, floating on the right
    if cover:
        fixed:
            xysize (560, 820)
            pos (1180, 120)
            at dl_cover_in
            add "gui/dl_glow.png" align (0.5, 0.5) matrixcolor TintMatrix(Color(cover_book.accent)) at dl_glow_pulse
            fixed:
                xysize (480, 720)
                align (0.5, 0.5)
                at dl_cover_float
                add "gui/dl_shadow.png" align (0.5, 0.5) offset (18, 24) matrixcolor TintMatrix("#000000") alpha 0.65
                add Transform(cover, fit="contain", xysize=(480, 720))

    # legibility gradient over the left side
    add "gui/dl_menu_fade.png"

    # title block: Deadlock lockup with "The Library Reread" (tools/make_logo.py)
    vbox:
        xpos 120 ypos 230
        spacing 0
        if dl_ui("library_logo"):
            add dl_ui("library_logo") fit "contain" xysize (720, 160) at dl_fade_in(0.0)
        elif dl_ui("deadlock_logo"):
            add dl_ui("deadlock_logo") fit "contain" xysize (640, 144) at dl_fade_in(0.0)
            text _("The Library Reread") style "dl_menu_title" at dl_fade_in(0.1)
        else:
            text _("The Library Reread") style "dl_menu_title" at dl_fade_in(0.1)

    # menu
    vbox:
        xpos 106 ypos 450
        spacing 4
        use dl_main_menu_item(_("Open the Library"), Start(), 0.35)
        use dl_main_menu_item(_("Load"), ShowMenu("load"), 0.42)
        use dl_main_menu_item(_("Preferences"), ShowMenu("preferences"), 0.49)
        use dl_main_menu_item(_("About"), ShowMenu("about"), 0.56)
        if renpy.variant("pc"):
            use dl_main_menu_item(_("Help"), ShowMenu("help"), 0.63)
            use dl_main_menu_item(_("Quit"), Quit(confirm=False), 0.70)

    # footer
    text _("Unofficial fan preservation  ·  Not affiliated with Valve Corporation  ·  v[config.version]"):
        style "dl_footer_note"
        xpos 120 ypos 1030
        at dl_fade_in(0.8)
