## The reading screen, rebuilt after Deadlock's book viewer:
##   citadel_db_page_book_reader / citadel_ui_book_viewer   (page area)
##   in-game capture of the reader                           (keyboard hint bar)
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

## Valve's reader has no on-screen arrows: just keyboard hints along the
## bottom (from an in-game capture of citadel_book_open):
##   [ESC] BACK      [<] BACK      [SPACE] PLAY      [>] NEXT
## Positions below are that capture scaled to 1920x1080.

## Colours / sizes measured from an in-game capture of Valve's reader
## (scaled to 1080p): caps 24px tall, labels ~19px, everything cream at
## ~35% (hover x1.3 and 2px lift, from citadel_dashboard_footer_bar).
## Fonts: measured against an in-game capture, the hints are a heavy
## grotesque (Arial Bold, Panorama's fallback). Liberation Sans Bold (SIL
## OFL, metric-identical to Arial): label 20px, caps 14px, sizes fitted to
## the capture's glyph widths (BACK 56px, ESC cap 44px, SPACE cap 64px).

define DL_HINT_IDLE  = "#5C564D"
define DL_HINT_HOVER = "#787064"
define DL_CAP_IDLE   = "#524D46"
define DL_CAP_HOVER  = "#6B645B"

transform dl_hint_lift:
    on idle:
        ease 0.1 yoffset 0
    on hover:
        ease 0.1 yoffset -2

style dl_hint_button is button:
    background None
    padding (0, 0)

style dl_hint_label is default:
    font "gui/fonts/LiberationSans-Bold.ttf"
    size 20
    idle_color DL_HINT_IDLE
    hover_color DL_HINT_HOVER
    selected_idle_color DL_HINT_HOVER
    selected_hover_color DL_HINT_HOVER

style dl_hint_cap is default:
    font "gui/fonts/LiberationSans-Bold.ttf"
    size 14
    color "#040503"

style dl_hint_capframe is frame:
    idle_background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix(DL_CAP_IDLE)), 4, 4)
    hover_background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix(DL_CAP_HOVER)), 4, 4)
    selected_idle_background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix(DL_CAP_HOVER)), 4, 4)
    ysize 24
    yalign 0.5

screen dl_keyhint(x, cap, label, act):
    button:
        style "dl_hint_button"
        pos (x, 1050)
        yanchor 0.5
        action act
        hbox:
            spacing 6
            at dl_hint_lift
            if cap in ("left", "right"):
                frame:
                    style "dl_hint_capframe"
                    padding (0, 0)
                    xsize 24
                    add ("gui/dl_tri_left.png" if cap == "left" else "gui/dl_tri_right.png") align (0.5, 0.5)
            else:
                frame:
                    style "dl_hint_capframe"
                    padding (7, 0)
                    text cap style "dl_hint_cap" align (0.5, 0.5)
            text label style "dl_hint_label" yalign 0.5

screen dl_reader():
    zorder 50

    $ choosing = dl_choice_showing()
    $ auto = _preferences.afm_enable
    $ leave = Confirm(_("Return to the chapter select?\nThis chapter will not be marked as finished."),
                      Jump("vn_leave_chapter"))

    use dl_keyhint(18, "ESC", _("BACK"), leave)
    key "K_ESCAPE" action leave

    # Valve hides back / play / next while a choice is on screen
    if not choosing:
        use dl_keyhint(540, "left", _("BACK"), Rollback())
        use dl_keyhint(900, "SPACE", (_("STOP") if auto else _("PLAY")), Preference("auto-forward", "toggle"))
        use dl_keyhint(1296, "right", _("NEXT"), Return(True))

        key "K_LEFT" action Rollback()
        key "K_RIGHT" action Return(True)
        key "K_SPACE" action Preference("auto-forward", "toggle")

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
