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
            tr = renpy.render(t, width, height, st, at)
            r = renpy.Render(width, height)
            r.blit(tr, (int((width - cw * z) / 2), int((height - ch * z) / 2)))
            return r
        def visit(self):
            return [self.child]

    def dl_modal_bg():
        """Valve's popup panel: paper_panel_bg_01 (cover) with the
        wipe_radial_1024x512 opacity mask, from popups_shared.css.
        Falls back to our generated texture if Valve's images aren't there."""
        if renpy.loadable("images/ui/popup_paper.png") and renpy.loadable("images/ui/popup_mask.png"):
            return AlphaMask(DLCover("images/ui/popup_paper.png"), DLCover("images/ui/popup_mask.png"))
        return Frame("gui/dl_modal.png", 0, 0)

define DL_MODAL_BODY_FONT = ("fonts/radiance-regular.otf" if renpy.loadable("fonts/radiance-regular.otf") else DL_BODY)

style dl_modal_frame is frame:
    background dl_modal_bg()
    xalign 0.5
    yalign 0.5
    xsize 600
    padding (28, 44, 28, 16)      # .PopupPanel padding 24 28 16 28 (+ title margin-top 20)

style dl_modal_title is default:
    font DL_SANS
    size 32                       # .PopupTitle 32px, offWhite&88
    color "#C2B6A4"
    xalign 0.5
    text_align 0.5
    kerning 1

style dl_modal_body is default:
    font DL_MODAL_BODY_FONT
    size 18                       # .PopupDesc: Label default 18px, offWhite&44
    color "#8C8476"
    xalign 0.5
    text_align 0.5
    line_spacing 6

style dl_pill_primary is button:
    background Frame(Transform("gui/dl_pill.png", matrixcolor=TintMatrix("#8F8779")), 23, 0)
    hover_background Frame(Transform("gui/dl_pill.png", matrixcolor=TintMatrix("#A9A091")), 23, 0)
    padding (28, 0)
    ysize 46                      # pill image is exactly 46px tall: clean round ends
    xminimum 150

style dl_pill_primary_text is default:
    font DL_SANS
    size 20
    yalign 0.5
    color "#1B1B19"
    xalign 0.5
    kerning 1

style dl_pill_secondary is dl_pill_primary:
    background Frame(Transform("gui/dl_pill.png", matrixcolor=TintMatrix("#615B52")), 23, 0)
    hover_background Frame(Transform("gui/dl_pill.png", matrixcolor=TintMatrix("#7A7368")), 23, 0)

style dl_pill_secondary_text is dl_pill_primary_text:
    color "#1B1B19"

style dl_modal_esc is frame:
    background Frame(Transform("gui/dl_keycap.png", matrixcolor=TintMatrix("#57524B")), 4, 4)
    padding (9, 0)
    ysize 28
    yalign 0.5

style dl_modal_esc_text is default:
    font "gui/fonts/LiberationSans-Bold.ttf"
    bold True
    size 14
    color "#1B1B19"

style dl_modal_close is default:
    font "gui/fonts/LiberationSans-Bold.ttf"
    bold True
    size 20                       # #EscapeButton > Label 20px
    color "#625D54"   # same muted tone as the ESC cap (sampled)

# Valve's popup open (popups_shared .PopupPanel.Hidden): scale 0.95 -> 1 and
# fade in over 0.2s
transform dl_popup_in(delay=0.0):
    alpha 0.0 zoom 0.95
    pause delay
    ease 0.2 alpha 1.0 zoom 1.0
