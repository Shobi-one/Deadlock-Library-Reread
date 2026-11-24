## The reading screen, rebuilt after Deadlock's book viewer:
##   citadel_db_page_book_reader / citadel_ui_book_viewer   (page area)
##   citadel_ui_book_nav_button_icon                         (prev / next / toc / history icons)
##   citadel_ui_book_nav_button_choice                       (image choice cards)
##   citadel_ui_book_nav_button                              (text nav buttons)
## Pages are shown in a 1700x956 viewer on black, 20px from the top.

define DL_VIEWER = (110, 20, 1700, 956)          # x, y, w, h

## ------------------------------------------------------------------
## Transforms
## ------------------------------------------------------------------

# Valve "fade_in_color_in": fade in grey, then the colour comes in
transform dl_page_color_in:
    alpha 0.0 matrixcolor SaturationMatrix(0.0)
    ease 0.4 alpha 1.0
    ease 0.4 matrixcolor SaturationMatrix(1.0)

# nav icons: opacity 0.2 -> 1 on hover
transform dl_nav_icon:
    on idle:
        ease 0.15 alpha 0.2
    on hover:
        ease 0.15 alpha 1.0
    on selected_idle:
        ease 0.15 alpha 0.6
    on selected_hover:
        ease 0.15 alpha 1.0

# choice card artwork: brightness 0.2 -> 1 on hover
transform dl_choice_art:
    on idle:
        ease 0.18 matrixcolor TintMatrix("#333333")
    on hover:
        ease 0.18 matrixcolor TintMatrix("#ffffff")

## ------------------------------------------------------------------
## Helpers
## ------------------------------------------------------------------

init python:

    def dl_icon(name, glyph, flip=False):
        """Valve's control icon if extracted, otherwise a text glyph."""
        path = dl_ui(name)
        if path:
            d = Transform(path, fit="contain", xysize=(50, 50))
            return Transform(d, xzoom=-1.0) if flip else d
        return Text(glyph, font="DejaVuSans.ttf", size=40, color="#FFEFD7",
                    xalign=0.5, yalign=0.5)

    def dl_choice_showing():
        return renpy.get_screen("choice") is not None

## ------------------------------------------------------------------
## Leaving a chapter halfway (table of contents button)
## ------------------------------------------------------------------

label vn_leave_chapter:
    hide screen dl_reader
    $ vn_page_art = False
    $ quick_menu = True
    $ renpy.pop_call()
    scene black with dissolve
    jump book_loop

## ------------------------------------------------------------------
## Reader overlay: shown while a chapter is playing
## ------------------------------------------------------------------

style dl_nav_icon_button is button:
    background None
    padding (0, 0)
    xysize (50, 50)

screen dl_reader():
    zorder 50

    $ vx, vy, vw, vh = DL_VIEWER
    $ choosing = dl_choice_showing()

    # Valve hides prev / next / auto while a choice is on screen
    if not choosing:
        button:
            style "dl_nav_icon_button"
            pos (vx // 2 - 25, vy + vh // 2 - 25)
            action Rollback()
            add dl_icon("arrow", "‹", flip=True) at dl_nav_icon

        button:
            style "dl_nav_icon_button"
            pos (vx + vw + (1920 - vx - vw) // 2 - 25, vy + vh // 2 - 25)
            action Return(True)
            add dl_icon("arrow", "›") at dl_nav_icon

    # bottom bar: table of contents + history (left), auto-play (right)
    hbox:
        pos (vx, vy + vh + 26)
        spacing 24
        button:
            style "dl_nav_icon_button"
            action Confirm(_("Return to the chapter select?\nThis chapter will not be marked as finished."),
                           Jump("vn_leave_chapter"))
            add dl_icon("toc", "≡") at dl_nav_icon
        button:
            style "dl_nav_icon_button"
            action ShowMenu("history")
            add dl_icon("history", "↺") at dl_nav_icon

    if not choosing:
        button:
            style "dl_nav_icon_button"
            pos (vx + vw - 50, vy + vh + 26)
            action Preference("auto-forward", "toggle")
            add Text(_("AUTO"), font=DL_SANS, size=18, color="#FFEFD7", kerning=2,
                     xalign=0.5, yalign=0.5) at dl_nav_icon

## ------------------------------------------------------------------
## Choices: Valve's 400x240 image cards over the right of the page
## ------------------------------------------------------------------

style dl_choice_prompt is dl_text:
    font DL_BOLD
    size 28
    text_align 0.5
    xalign 0.5
    yalign 0.5
    xmaximum 360
    outlines [(0, "#000000", 1, 1)]

style dl_navtext_button is button:
    background Frame("gui/dl_navbtn.png", 0, 0)
    hover_background Frame("gui/dl_navbtn_hover.png", 0, 0)
    padding (20, 10)

style dl_navtext_button_text is dl_text:
    font DL_BODY
    size 32
    idle_color "#FFEFD7cc"
    hover_color "#FFEFD7"

screen choice(items):
    style_prefix "choice"

    $ vx, vy, vw, vh = DL_VIEWER
    $ cards = [i for i in items if i.kwargs.get("kind") != "nav"]
    $ navs = [i for i in items if i.kwargs.get("kind") == "nav"]

    # Valve: list area = viewer minus margins 450 left, 200 top, 50 right/bottom
    fixed:
        pos (vx + 450, vy + 200)
        xysize (vw - 500, vh - 250)

        hbox:
            align (0.5, 0.5)
            box_wrap True
            spacing 60
            box_wrap_spacing 60

            for n, i in enumerate(cards):
                $ thumb = i.kwargs.get("thumb", "")
                button:
                    xysize (402, 242)
                    padding (1, 1)
                    background Solid("#ffffff")
                    hover_background Solid("#ffffff")
                    action i.action
                    at dl_fade_up(0.05 + 0.08 * n)
                    fixed:
                        xysize (400, 240)
                        add Solid("#000000")
                        if thumb and renpy.loadable(thumb):
                            add dl_thumb(thumb, (400, 240)) at dl_choice_art
                        else:
                            add Solid("#16181c")
                        text i.caption style "dl_choice_prompt"

    # text-style nav buttons (e.g. back to chapter select), under the page
    if navs:
        hbox:
            xalign 0.5
            ypos vy + vh + 14
            spacing 20
            for i in navs:
                textbutton i.caption:
                    style "dl_navtext_button"
                    action i.action
