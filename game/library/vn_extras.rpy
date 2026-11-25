## Restoration Extras: additions that are NOT what Valve shipped.
## Each one is listed here, off by default, and toggled from the Extras menu,
## so the default game stays 100% Valve.
##
## To add one: append an entry to VN_EXTRAS (ready=False shows it as
## "Coming soon"), then check it in the game with vn_extra_on("<id>").

default persistent.vn_extras_on = set()
default persistent.vn_extras = False           # old single toggle (v1.1 beta)

init -1 python:
    VN_EXTRAS = [
        dict(id="infernus_voices", ready=True,
             title=_("Infernus book: Lady Geist's voice lines"),
             desc=_("The Infernus book opens with the same scene as Lady Geist's chapter 3b, "
                    "\"Hunger Strike\". Valve shipped this book without sound; this extra plays "
                    "Geist's matching 3b voice lines on those pages.")),
        dict(id="hud_2026", ready=True,
             title=_("Interface: 2026 style"),
             desc=_("Swaps the reader's key hints from the 2024 version (the Library while it was live) "
                    "to the leftover version still in today's Deadlock (four hints in capitals, dimmed, "
                    "in the game's fallback font), and pop-ups to today's paper-style dialog.")),
        dict(id="dynamo_fred", ready=False,
             title=_("Dynamo's original voice (Fred Tatasciore)"),
             desc=_("Dynamo was first voiced by Fred Tatasciore before Valve re-recorded his lines "
                    "with John Patrick Lowrie. Plays Fred's original takes from the May 2024 build, "
                    "including the complete \"Medieval History\" line.")),
        dict(id="patron_voices", ready=False,
             title=_("Patron voices: Hidden King / Archmother"),
             desc=_("Unused recordings of the Patron's lines in Lady Geist's chapters 5g, 5h and 5i, "
                    "voiced by the Hidden King and the Archmother.")),
    ]

    def vn_extra_on(extra_id):
        return extra_id in persistent.vn_extras_on

    def vn_extra_voice(filename, extra_id="infernus_voices"):
        """Queue a voice line only when that extra is switched on."""
        if vn_extra_on(extra_id):
            voice(filename)

    class VNToggleExtra(Action):
        def __init__(self, extra_id):
            self.extra_id = extra_id
        def __call__(self):
            s = set(persistent.vn_extras_on)
            s.symmetric_difference_update([self.extra_id])
            persistent.vn_extras_on = s
            renpy.restart_interaction()
        def get_selected(self):
            return vn_extra_on(self.extra_id)

init 1 python:
    # carry over the earlier single "Restoration Extras" toggle
    if persistent.vn_extras and "infernus_voices" not in persistent.vn_extras_on:
        persistent.vn_extras_on = set(persistent.vn_extras_on) | {"infernus_voices"}
        persistent.vn_extras = False

## ------------------------------------------------------------------
## Extras menu
## ------------------------------------------------------------------

style vn_extra_title is dl_text:
    font DL_SERIF
    size 30
    color "#FFEFD7"

style vn_extra_desc is dl_text:
    size 20
    color "#FFEFD7aa"
    line_spacing 4

style vn_extra_soon is dl_text:
    font DL_SANS
    size 15
    color "#7CBC1D"
    kerning 2

screen extras():
    tag menu
    use game_menu(_("Extras"), scroll="viewport"):
        vbox:
            spacing 0
            xsize 1000
            text _("Restoration Extras add things Valve didn't ship: recordings it made but never used here, or small reconstructions. Everything is off by default, so the game stays exactly as Valve left it.") style "vn_extra_desc" color "#FFEFD7cc"
            null height 40
            for e in VN_EXTRAS:
                hbox:
                    spacing 24
                    if e["ready"]:
                        textbutton (_("On") if vn_extra_on(e["id"]) else _("Off")):
                            style "check_button"
                            action VNToggleExtra(e["id"])
                            xsize 110
                            yalign 0.0
                    else:
                        text _("COMING SOON") style "vn_extra_soon" xsize 110 yoffset 10
                    vbox:
                        spacing 8
                        xsize 860
                        text e["title"] style "vn_extra_title" color ("#FFEFD7" if e["ready"] else "#FFEFD766")
                        text e["desc"] style "vn_extra_desc"
                null height 34
