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
    $ vn_stop_skip()
    hide screen dl_reader
    $ vn_page_art = False
    $ quick_menu = False
    $ renpy.pop_call()
    scene black with dissolve
    jump book_loop

## ------------------------------------------------------------------
## Reader overlay: shown while a chapter is playing
## ------------------------------------------------------------------

## Rebuilt 1:1 from Valve's reader running in the 25 May 2024 build (4,192),
## while the Library was a live feature (scaled to 1920x1080):
##   [ESC] Back (x 52)          [->] Next (x 891)          [Space] Play (x 1716)
## - caps #53504F, near-square; ESC/Space 31px tall, the Next cap 53x35 with a
##   white arrow; cap text Retail Demo Bold 18 in offWhite
## - labels Retail Demo 18, offWhite, 12px after the cap, title case
## - centre: [->] Next alone on a chapter's first page (x 891); otherwise the
##   pair [<-] Back (817) + [->] Next (963); at a choice only [<-] Back (891)

## Fonts from the May 2024 build's own style sheets: base.css sets the root
## font to "Retail Demo"; Label = 18px; .controlKeyBind = bold, padding
## 10px left/right + 2px top, min 32x32 (citadel_db_page_shared.css).
define DL_HINT_FONT     = ("fonts/retaildemo-regular.otf" if renpy.loadable("fonts/retaildemo-regular.otf")
                           else "gui/fonts/LiberationSans-Bold.ttf")
define DL_HINT_CAP_FONT = ("fonts/retaildemo-bold.otf" if renpy.loadable("fonts/retaildemo-bold.otf")
                           else "gui/fonts/LiberationSans-Bold.ttf")
define DL_CAP_COLOR = "#53504F"

# hover, from the May 2024 build (citadel_db_page_shared.css,
# #FooterBar .FooterCommand:hover): brightness 1.3 + translateY(-2px),
# 0.1s ease
transform dl_hint_fade:
    on idle:
        ease 0.1 matrixcolor BrightnessMatrix(0.0) yoffset 0
    on hover:
        ease 0.1 matrixcolor BrightnessMatrix(0.12) yoffset -2

style dl_hint_button is button:
    background None
    padding (0, 0)

style dl_hint_label is default:
    font DL_HINT_FONT
    size 18
    color "#FFEFD7"

style dl_hint_cap is default:
    font DL_HINT_CAP_FONT
    size 18
    color "#FFEFD7"

style dl_hint_capframe is frame:
    background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix(DL_CAP_COLOR)), 2, 2)
    ysize 32
    yalign 0.5

screen dl_keyhint(x, cap, label, act):
    button:
        style "dl_hint_button"
        pos (x, 1012)
        action act
        hbox:
            spacing 12
            at dl_hint_fade
            if cap in ("left", "right"):
                frame:
                    style "dl_hint_capframe"
                    xysize (53, 36)
                    padding (0, 0)
                    add ("gui/dl_arrow_%s.png" % cap) align (0.5, 0.5)
            else:
                frame:
                    style "dl_hint_capframe"
                    padding (10, 2, 10, 0)            # .controlKeyBind padding
                    text cap style "dl_hint_cap" align (0.5, 0.5)
            text label style "dl_hint_label" yalign 0.5

screen dl_reader():
    zorder 50

    $ choosing = dl_choice_showing()
    $ auto = _preferences.afm_enable
    $ nav = dl_choice_nav()
    $ leave = nav or Confirm(_("Return to the chapter select?\nThis chapter will not be marked as finished."),
                             Jump("vn_leave_chapter"))

    use dl_keyhint(52, "ESC", vn_str("reader_prev"), leave)     # footer padding 50 + margin 2
    key "K_ESCAPE" action leave

    # Centre group (Valve, May 2024): a lone hint sits at x 891; when both
    # are shown, [<-] Back at 817 and [->] Next at 963 (centred pair).
    # First page of a chapter: no Back. At a choice: Back only, no Play.
    if choosing:
        if not vn_page_first:
            use dl_keyhint(891, "left", vn_str("reader_prev"), Rollback())
            key "K_LEFT" action Rollback()
    else:
        if vn_page_first:
            use dl_keyhint(891, "right", vn_str("reader_next"), Return(True))
        else:
            use dl_keyhint(817, "left", vn_str("reader_prev"), Rollback())
            use dl_keyhint(963, "right", vn_str("reader_next"), Return(True))
            key "K_LEFT" action Rollback()
        use dl_keyhint(1716, "Space", (vn_str("reader_pause") if auto else vn_str("reader_play")), Preference("auto-forward", "toggle"))

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
    on "show" action Function(vn_stop_skip)      # skipped to the chapter's end

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
                    # a branch locked by an earlier choice can't be picked
                    action (NullAction() if state == "unreachable" else i.action)
                    at dl_fade_up(0.05 + 0.08 * n)
                    fixed:
                        xysize (400, 240)
                        add Solid("#444444" if state == "unreachable" else "#000000")
                        if thumb and renpy.loadable(thumb) and state != "unreachable":
                            add dl_thumb(thumb, (400, 240)) at dl_choice_art(state == "unlockable")
                        text i.caption style "dl_choice_prompt"
                        if state != "unlocked" and dl_ui("lock"):
                            add dl_ui("lock") xysize (20, 20) align (1.0, 1.0) offset (-10, -10)

## ------------------------------------------------------------------
## Centred text for books without page art (screens.rpy -> screen say)
## ------------------------------------------------------------------

style vn_center_frame is frame:
    background Solid("#0a0a09c8")
    xalign 0.5
    yalign 0.44
    xsize 1300
    ymaximum 820
    padding (70, 44, 70, 48)

style vn_center_who is default:
    font DL_SERIF
    size 40
    color "#7CBC1D"

style vn_center_what is default:
    font DL_BODY
    color "#FFEFD7"
    line_spacing 6

