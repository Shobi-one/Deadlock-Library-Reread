## First-launch disclaimer: what this project is, and why parts are missing.
## Shown once (persistent.dl_seen_disclaimer); also reachable from About.

default persistent.dl_seen_disclaimer = False

label splashscreen:
    if not persistent.dl_seen_disclaimer:
        scene black
        call screen dl_disclaimer
        $ persistent.dl_seen_disclaimer = True
        scene black with dissolve
    return

style dl_disclaimer_title is dl_text:
    font DL_SERIF
    size 52

style dl_disclaimer_text is dl_text:
    size 24
    color "#FFEFD7d9"
    line_spacing 6

style dl_disclaimer_small is dl_text:
    size 17
    color "#FFEFD780"
    line_spacing 4

screen dl_disclaimer(from_menu=False):
    modal True
    zorder 200
    # first boot: called from splashscreen -> Return(); from About: shown on
    # top of the menu -> just hide it
    $ done = Hide("dl_disclaimer") if from_menu else Return()

    add Solid("#000000")
    if dl_ui("library_bg"):
        add Transform(dl_ui("library_bg"), fit="cover", xysize=(1920, 1080), alpha=0.15)

    frame:
        xalign 0.5 yalign 0.5
        xsize 1040
        background dl_modal_bg()          # Valve's popup paper + soft edge mask
        padding (90, 72, 90, 64)
        at dl_popup_in(0.1)

        vbox:
            spacing 0
            if dl_ui("library_logo"):
                add dl_ui("library_logo") fit "contain" xysize (460, 100)
                null height 36
            text _("Before you start reading") style "dl_disclaimer_title"
            null height 14
            add Solid(dl_green, xysize=(90, 3))
            null height 28

            text _("The Library Reread brings back {b}the Library{/b}: the visual novels Valve made for Deadlock in 2024 and later removed from the game."):
                style "dl_disclaimer_text"
            null height 18
            text _("Everything here was recovered from old game builds and community archives. Valve never finished the Library, so the books are in different states. Only Lady Geist's and Infernus's books were ever illustrated; Ivy's and Holliday's were voiced and written but {b}never got artwork{/b}, and some pages are missing {b}voice lines{/b} or {b}sound effects{/b}."):
                style "dl_disclaimer_text"
            null height 18
            text _("Expect rough edges. That is part of what is being preserved."):
                style "dl_disclaimer_text"
                italic True

            null height 34
            text _("Unofficial fan preservation project, not affiliated with or endorsed by Valve Corporation. Deadlock and all of its characters, art, writing and audio are the property of Valve."):
                style "dl_disclaimer_small"

            null height 34
            textbutton _("CONTINUE"):
                style "dl_unlock_button"
                text_size 24
                padding (40, 14)
                xalign 1.0
                action done

    key "K_RETURN" action done
    key "K_SPACE" action done
    if from_menu:
        key "game_menu" action done
