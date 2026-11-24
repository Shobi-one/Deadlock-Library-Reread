## Deadlock styling for the game menus (Save, Load, Preferences, History,
## About, Help) and the confirm dialog. Loaded after screens.rpy so these
## override its default styles. Layout lives in screens.rpy -> game_menu.

init offset = 1

## ------------------------------------------------------------------
## Frame: dark content panel on the right, like the Library shelf
## ------------------------------------------------------------------

style game_menu_content_frame:
    xpos 620 ypos 0
    xsize 1200 ysize 1080
    background Solid("#10130Dee")
    left_padding 70
    right_padding 50
    top_padding 110
    bottom_padding 90
    left_margin 0
    right_margin 0
    top_margin 0

style game_menu_viewport:
    xsize 1060

style game_menu_side:
    spacing 15

## ------------------------------------------------------------------
## Navigation (left column)
## ------------------------------------------------------------------

style navigation_button:
    background None
    hover_background None
    left_padding 18
    top_padding 4
    bottom_padding 4
    foreground None
    selected_foreground Transform(Solid("#65951D", xysize=(4, 30)), yalign=0.5)

style navigation_button_text:
    font DL_SANS
    size 32
    kerning 2
    xalign 0.0
    idle_color "#FFEFD7a6"
    hover_color "#FFEFD7"
    selected_color "#FFEFD7"
    insensitive_color "#FFEFD740"

## ------------------------------------------------------------------
## Labels and plain text
## ------------------------------------------------------------------

style gui_label_text:
    font DL_SERIF
    color "#65951D"

style pref_label:
    top_margin 24
    bottom_margin 10

style pref_label_text:
    font DL_SERIF
    size 26
    color "#65951D"

style about_label_text:
    font DL_SERIF
    color "#FFEFD7"

style help_label_text:
    font DL_SANS
    size 24
    color "#65951D"

style help_text:
    font DL_BODY
    size 24

## ------------------------------------------------------------------
## Radio and check buttons: small squares instead of Ren'Py's blue art
## ------------------------------------------------------------------

style radio_button:
    background None
    left_padding 34
    foreground Transform(Solid("#FFEFD733", xysize=(16, 16)), yalign=0.5)
    hover_foreground Transform(Solid("#FFEFD780", xysize=(16, 16)), yalign=0.5)
    selected_foreground Transform(Solid("#7CBC1D", xysize=(16, 16)), yalign=0.5)
    selected_hover_foreground Transform(Solid("#9BE02A", xysize=(16, 16)), yalign=0.5)

style check_button:
    background None
    left_padding 34
    foreground Transform(Solid("#FFEFD733", xysize=(16, 16)), yalign=0.5)
    hover_foreground Transform(Solid("#FFEFD780", xysize=(16, 16)), yalign=0.5)
    selected_foreground Transform(Solid("#7CBC1D", xysize=(16, 16)), yalign=0.5)
    selected_hover_foreground Transform(Solid("#9BE02A", xysize=(16, 16)), yalign=0.5)

style radio_button_text:
    font DL_BODY
    size 24
    idle_color "#FFEFD7a6"
    hover_color "#FFEFD7"
    selected_color "#FFEFD7"
    selected_hover_color "#FFEFD7"

style check_button_text:
    font DL_BODY
    size 24
    idle_color "#FFEFD7a6"
    hover_color "#FFEFD7"
    selected_color "#FFEFD7"
    selected_hover_color "#FFEFD7"

style slider_button_text:
    font DL_SANS
    size 22
    idle_color "#FFEFD7a6"
    hover_color "#FFEFD7"

## ------------------------------------------------------------------
## Sliders and scrollbars
## ------------------------------------------------------------------

style slider:
    ysize 24
    base_bar None
    left_bar Solid("#65951D")
    right_bar Solid("#FFEFD71f")
    thumb Solid("#FFEFD7", xysize=(6, 24))
    hover_thumb Solid("#FFFFFF", xysize=(6, 24))

style slider_slider:
    xsize 420

style vscrollbar:
    xsize 8
    base_bar Solid("#FFEFD714")
    thumb Solid("#FFEFD759")
    hover_thumb Solid("#65951D")
    unscrollable "hide"

style scrollbar:
    ysize 8
    base_bar Solid("#FFEFD714")
    thumb Solid("#FFEFD759")
    hover_thumb Solid("#65951D")
    unscrollable "hide"

## ------------------------------------------------------------------
## Save / Load slots
## ------------------------------------------------------------------

style slot_button:
    background Solid("#FFEFD70a")
    hover_background Solid("#65951D33")
    selected_background Solid("#65951D22")
    padding (14, 14)

style slot_button_text:
    font DL_BODY
    size 18
    idle_color "#FFEFD7b3"
    hover_color "#FFEFD7"
    selected_idle_color "#FFEFD7"
    selected_hover_color "#FFEFD7"

style page_label_text:
    font DL_SERIF
    size 30
    color "#FFEFD7"
    hover_color "#65951D"

style page_button:
    background None
    padding (14, 6)

style page_button_text:
    font DL_SANS
    size 24
    idle_color "#FFEFD7a6"
    hover_color "#FFEFD7"
    selected_color "#7CBC1D"

## ------------------------------------------------------------------
## Confirm dialog (Quit? / Overwrite save? ...)
## ------------------------------------------------------------------

style confirm_frame:
    background Solid("#10130Df2")
    padding (70, 50)

style confirm_prompt_text:
    font DL_BODY
    size 30
    color "#FFEFD7"

style confirm_button_text:
    font DL_SANS
    size 30
    idle_color "#FFEFD7a6"
    hover_color "#FFEFD7"
