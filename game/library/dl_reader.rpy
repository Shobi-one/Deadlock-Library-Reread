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

# choice card #Icon: brightness 0.2, 1 on hover (instant in Valve's CSS);
# not-yet-unlocked chapters are also desaturated
transform dl_choice_art(grey=False):
    on idle:
        matrixcolor TintMatrix("#333333") * SaturationMatrix(0.0 if grey else 1.0)
    on hover:
        matrixcolor TintMatrix("#ffffff") * SaturationMatrix(0.0 if grey else 1.0)

## ------------------------------------------------------------------
## Helpers
## ------------------------------------------------------------------

init python:

    def dl_choice_showing():
        return renpy.get_screen("choice") is not None

    def dl_choice_nav():
        """The 'back to chapter select' action of the current chapter-end
        menu, if any (Valve has no button for it: ESC does that)."""
        scr = renpy.get_screen("choice")
        if scr is None:
            return None
        for i in scr.scope.get("items", []):
            if i.kwargs.get("kind") == "nav":
                return i.action
        return None

    def dl_choice_state(i):
        """unlocked / unlockable / unreachable for a chapter-end choice,
        mirroring Valve's IsUnlockable / Unlocked / NotReachable classes."""
        cid = i.kwargs.get("chapter")
        bid = getattr(store, "lib_book_id", None)
        if not cid or not bid:
            return "unlocked"
        try:
            book = vn_book(bid)
            return dl_node_state(book, book.chapter(cid))
        except Exception:
            return "unlocked"

## ------------------------------------------------------------------
## Leaving a chapter halfway (table of contents button)
## ------------------------------------------------------------------

label vn_leave_chapter:
    hide screen dl_reader
    $ vn_page_art = False
    $ quick_menu = False
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
## Fonts: Valve's CSS asks for Radiance (base.css), but the live game draws
## this footer in a bold Arial-style grotesque (side-by-side captures). We
## match what's on screen: Liberation Sans Bold (SIL OFL, Arial metrics),
## sized from the capture (BACK 56px wide, ESC cap 44px, SPACE cap 64px).
## The game's text is heavier than Arial Bold (the engine emboldens it again),
## so both styles also set bold True for Ren'Py's synthetic bold.
define DL_HINT_FONT = "gui/fonts/LiberationSans-Bold.ttf"
define DL_HINT_CAP_FONT = "gui/fonts/LiberationSans-Bold.ttf"

define DL_HINT_IDLE  = "#5C564D"
define DL_HINT_HOVER = "#787064"
define DL_CAP_IDLE   = "#524D46"
define DL_CAP_HOVER  = "#6B645B"

# hover: colour fades lighter (no movement). Everything is drawn in the
# hover colours and dimmed to the idle ones (#5C564D / #787064 = 0.77).
transform dl_hint_fade:
    on idle:
        ease 0.15 matrixcolor TintMatrix("#c4c4c4")
    on hover:
        ease 0.15 matrixcolor TintMatrix("#ffffff")

style dl_hint_button is button:
    background None
    padding (0, 0)

style dl_hint_label is default:
    font DL_HINT_FONT
    size 20
    bold True          # Panorama draws bold-on-bold: synthetic emboldening
    color DL_HINT_HOVER
    selected_idle_color DL_HINT_HOVER
    selected_hover_color DL_HINT_HOVER

style dl_hint_cap is default:
    font DL_HINT_CAP_FONT
    size 13
    bold True
    color "#040503"

style dl_hint_capframe is frame:
    idle_background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix(DL_CAP_HOVER)), 4, 4)
    hover_background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix(DL_CAP_HOVER)), 4, 4)
    selected_idle_background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix(DL_CAP_HOVER)), 4, 4)
    ysize 25
    yalign 0.5

screen dl_keyhint(x, cap, label, act):
    button:
        style "dl_hint_button"
        pos (x, 1050)
        yanchor 0.5
        action act
        hbox:
            spacing 6
            at dl_hint_fade
            if cap in ("left", "right"):
                frame:
                    style "dl_hint_capframe"
                    padding (0, 0)
                    xsize 25
                    # Valve's glyph (panorama/images/glyphs/keyboard_arrow_*), white
                    # on a 148px canvas: shown full-cap and tinted to the key text
                    # colour. Falls back to our own triangle if not extracted.
                    $ glyph = dl_ui("glyph_arrow_" + cap)
                    if glyph:
                        add Transform(glyph, xysize=(24, 24), matrixcolor=TintMatrix("#040503")) align (0.5, 0.5)
                    else:
                        add ("gui/dl_tri_left.png" if cap == "left" else "gui/dl_tri_right.png") align (0.5, 0.5)
            else:
                frame:
                    style "dl_hint_capframe"
                    padding (8, 0)
                    text cap style "dl_hint_cap" align (0.5, 0.5)
            text label style "dl_hint_label" yalign 0.5

screen dl_reader():
    zorder 50

    $ choosing = dl_choice_showing()
    $ auto = _preferences.afm_enable
    $ nav = dl_choice_nav()
    $ leave = nav or Confirm(_("Return to the chapter select?\nThis chapter will not be marked as finished."),
                             Jump("vn_leave_chapter"))

    use dl_keyhint(18, "ESC", vn_str("reader_prev").upper(), leave)
    key "K_ESCAPE" action leave

    # Valve: no previous-page hint on a chapter's first page (back="0");
    # while choices are up, only BACK stays (play / next are hidden)
    if not vn_page_first:
        use dl_keyhint(540, "left", vn_str("reader_prev").upper(), Rollback())
        key "K_LEFT" action Rollback()

    if not choosing:
        use dl_keyhint(900, "SPACE", (vn_str("reader_pause") if auto else vn_str("reader_play")).upper(), Preference("auto-forward", "toggle"))
        use dl_keyhint(1296, "right", vn_str("reader_next").upper(), Return(True))

        key "K_RIGHT" action Return(True)
        key "K_SPACE" action Preference("auto-forward", "toggle")

## ------------------------------------------------------------------
## Choices, from citadel_ui_book_viewer + citadel_ui_book_nav_button_choice:
##   .PageChoiceListContainer  margins 450 left, 200 top, 50 right/bottom
##   #PageChoiceList           centred, flow right-wrap
##   #NavButton                400x240, 1px border, margin 30
##   #Icon                     page art, brightness 0.2 (1 on hover)
##   .Prompt                   28px bold, centred, text-shadow 1px 1px 3px
##   states: unlocked = white border; unlockable = yellow border, grey art,
##   lock icon bottom-right; unreachable = #444 bg, red border
##   The lock is red when the player can't afford it and white (.CanAfford)
##   when they can. There is no key economy in this restoration, so the
##   player can always afford it: white lock.
## Valve has no "back to chapter select" button: ESC does that, so the
## nav item from the converter is wired to ESC instead of drawn.
## ------------------------------------------------------------------

define DL_CHOICE_BORDER = {"unlocked": "#ffffff", "unlockable": "#ffff00", "unreachable": "#ff0000"}

# font + colour confirmed from an in-game capture: Valve's "sans" in offWhite
style dl_choice_prompt is default:
    font DL_SANS
    size 28
    color "#FFEFD7"
    text_align 0.5
    xalign 0.5
    yalign 0.5
    xmaximum 380
    outlines [(3, "#00000066", 1, 1), (1, "#000000cc", 1, 1)]

screen choice(items):
    style_prefix "choice"

    $ vx, vy, vw, vh = DL_VIEWER
    $ cards = [i for i in items if i.kwargs.get("kind") != "nav"]

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
                $ state = dl_choice_state(i)
                button:
                    xysize (402, 242)
                    padding (1, 1)
                    background Solid(DL_CHOICE_BORDER[state])
                    action i.action
                    at dl_fade_up(0.05 + 0.08 * n)
                    fixed:
                        xysize (400, 240)
                        add Solid("#444444" if state == "unreachable" else "#000000")
                        if thumb and renpy.loadable(thumb) and state != "unreachable":
                            add dl_thumb(thumb, (400, 240)) at dl_choice_art(state == "unlockable")
                        text i.caption style "dl_choice_prompt"
                        if state != "unlocked" and dl_ui("lock"):
                            add dl_ui("lock") xysize (20, 20) align (1.0, 1.0) offset (-10, -10)
