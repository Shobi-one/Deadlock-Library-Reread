## Deadlock-style confirm dialog (screens.rpy -> screen confirm).
## Colours sampled from an in-game capture of Valve's Player Feedback popup.
## Panel texture and pill shape are generated (gui/dl_modal.png, gui/dl_pill.png).

init -1 python:
    def dl_smallcaps(s):
        """Valve's buttons use small caps: first letter full size, rest smaller."""
        out = []
        for w in s.split(" "):
            if w:
                out.append(w[0].upper() + "{size=-6}" + w[1:].upper() + "{/size}")
        return " ".join(out)

    class DLCover(renpy.Displayable):
        """Scale a child to cover whatever size it's rendered at (CSS
        background-size: cover), cropping the overflow evenly."""
        def __init__(self, child, **kw):
            super(DLCover, self).__init__(**kw)
            self.child = renpy.displayable(child)
        def render(self, width, height, st, at):
            cr = renpy.render(self.child, width, height, st, at)
            cw, ch = cr.get_size()
            if not cw or not ch:
                return renpy.Render(width, height)
            z = max(float(width) / cw, float(height) / ch)
            t = Transform(self.child, zoom=z)
            tr = renpy.render(t, cw * z, ch * z, st, at)
            tw, th = tr.get_size()
            # crop the overflow (a plain blit isn't clipped to the panel)
            ox = max(0, int((tw - width) / 2))
            oy = max(0, int((th - height) / 2))
            return tr.subsurface((ox, oy, min(width, tw), min(height, th)))
        def visit(self):
            return [self.child]

    def dl_modal_bg():
        """Valve's popup panel: paper_panel_bg_01 (cover) with the
        wipe_radial_1024x512 opacity mask, from popups_shared.css.
        Falls back to our generated texture if Valve's images aren't there."""
        if renpy.loadable("images/ui/popup_paper.png") and renpy.loadable("images/ui/popup_mask.png"):
            return AlphaMask(DLCover("images/ui/popup_paper.png"), DLCover("images/ui/popup_mask.png"))
        return Frame("gui/dl_modal.png", 0, 0)

## Confirm dialog rebuilt from Valve's generic popup in the May 2024 build
## (popups/popup_generic.vxml + popups_shared.css + citadel_base_styles.css):
##   .PopupPanel   bg #231F20 + bg_smoke texture at 30%, 5px #7A7A7A border
##                 top and bottom, padding 32/64, min-width 450
##   #TitleLabel   .h2.display.silvered: Forevs Demo bold 50px, #C6C6C6
##   #MessageLabel .body_md.silvered: 20px medium, 80% opacity, max 450 wide
##   .PopupButton  pill, 2px border silvered&50, label 18px semi-bold
##                 silvered&90; hover: fill offWhite&60, label offBlack
##   open: fade in from scale 1.25 and 10px up

define DL_POPUP_SANS_MED  = _dl_demo_group("fonts/retaildemo-medium.otf", "fonts/reaver-regular.otf")
define DL_POPUP_SANS_SEMI = _dl_demo_group("fonts/retaildemo-semibold.otf", "fonts/reaver-semibold.otf")

init -1 python:
    def dl_popup_bg():
        layers = [Solid("#231F20")]
        if renpy.loadable("images/ui/popup_smoke.png"):
            layers.append(Transform(DLCover("images/ui/popup_smoke.png"), alpha=0.3))
        # border-top / border-bottom: 5px solid #7A7A7A
        layers.append(Solid("#7A7A7A", ysize=5, yalign=0.0))
        layers.append(Solid("#7A7A7A", ysize=5, yalign=1.0))
        return Fixed(*layers)

style dl_modal_frame is frame:
    background dl_popup_bg()
    xalign 0.5
    yalign 0.5
    xminimum 450
    padding (64, 32, 64, 32)

style dl_modal_rule is default

style dl_modal_title is default:
    font DL_SERIF
    size 50
    color "#C6C6C6"
    xalign 0.5
    text_align 0.5

style dl_modal_body is default:
    font DL_POPUP_SANS_MED
    size 20
    color "#C6C6C6cc"
    xalign 0.5
    text_align 0.5
    xmaximum 450

style dl_popup_button is button:
    background Frame(Transform("gui/dl_pill_line.png", matrixcolor=TintMatrix("#C6C6C6"), alpha=0.31), 20, 0)
    hover_background Fixed(Frame(Transform("gui/dl_pill_fill.png", matrixcolor=TintMatrix("#FFEFD7"), alpha=0.376), 20, 0),
                           Frame(Transform("gui/dl_pill_line.png", matrixcolor=TintMatrix("#C6C6C6"), alpha=0.31), 20, 0))
    ysize 40
    padding (25, 0)                 # 10px button + 15px label padding
    xminimum 40

style dl_popup_button_text is default:
    font DL_POPUP_SANS_SEMI
    size 18
    idle_color "#C6C6C6e6"
    hover_color "#10130D"
    xalign 0.5
    yalign 0.5
    yoffset -1

# Valve's popup open (popups_shared .PopupPanel.Hidden): scale 0.95 -> 1 and
# fade in over 0.2s
transform dl_popup_in(delay=0.0):
    alpha 0.0 zoom 1.25 yoffset -10
    pause delay
    ease 0.2 alpha 1.0 zoom 1.0 yoffset 0

## ------------------------------------------------------------------
## 2026 pop-up (Restoration Extra "hud_2026"): today's Deadlock pop-up
## (popups_shared + citadel_popup_player_feedback, current build):
## paper texture with a radial edge mask, 600px wide, uppercase 32px title,
## 18px body, filled pill buttons, faded ESC CLOSE hint.
## ------------------------------------------------------------------

define DL26_BODY_FONT = ("fonts/radiance-regular.otf" if renpy.loadable("fonts/radiance-regular.otf") else DL_BODY)

transform dl26_popup_in:
    alpha 0.0 zoom 0.95
    ease 0.2 alpha 1.0 zoom 1.0

style dl26_modal_frame is frame:
    background dl_modal_bg()
    xalign 0.5
    yalign 0.5
    xsize 600
    padding (28, 44, 28, 16)

style dl26_modal_title is default:
    font DL_SANS
    size 32
    color "#C2B6A4"
    xalign 0.5
    text_align 0.5
    kerning 1

style dl26_modal_body is default:
    font DL26_BODY_FONT
    size 18
    color "#8C8476"
    xalign 0.5
    text_align 0.5
    line_spacing 6

style dl26_pill is button:
    background Frame(Transform("gui/dl_pill.png", matrixcolor=TintMatrix("#8F8779")), 23, 0)
    hover_background Frame(Transform("gui/dl_pill.png", matrixcolor=TintMatrix("#A9A091")), 23, 0)
    ysize 46
    padding (28, 0)
    xminimum 150

style dl26_pill_text is default:
    font DL_SANS
    size 20
    color "#1B1B19"
    xalign 0.5
    yalign 0.5

style dl26_pill_dark is dl26_pill:
    background Frame(Transform("gui/dl_pill.png", matrixcolor=TintMatrix("#615B52")), 23, 0)
    hover_background Frame(Transform("gui/dl_pill.png", matrixcolor=TintMatrix("#7A7368")), 23, 0)

style dl26_pill_dark_text is dl26_pill_text

style dl26_esc is frame:
    background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix("#57524B")), 4, 4)
    padding (9, 0)
    ysize 28
    yalign 0.5

style dl26_esc_text is default:
    font "gui/fonts/LiberationSans-Bold.ttf"
    bold True
    size 14
    color "#1B1B19"

style dl26_close is default:
    font "gui/fonts/LiberationSans-Bold.ttf"
    bold True
    size 20
    color "#625D54"

screen dl26_confirm_panel(title, body, yes_action, no_action):
    frame:
        style "dl26_modal_frame"
        at dl26_popup_in
        vbox:
            xalign 0.5
            text title.upper() style "dl26_modal_title"
            if body:
                null height 16
                text body style "dl26_modal_body"
            null height 32
            hbox:
                xalign 0.5
                spacing 22
                textbutton dl_smallcaps(_("Yes")) style "dl26_pill" action yes_action
                textbutton dl_smallcaps(_("No")) style "dl26_pill_dark" action no_action
            null height 66
            button:
                style "dl_hint_button"
                xalign 0.5
                action no_action
                hbox:
                    spacing 8
                    at dl26_fade
                    frame:
                        style "dl26_esc"
                        text "ESC" style "dl26_esc_text" align (0.5, 0.5)
                    text _("CLOSE") style "dl26_close" yalign 0.5
