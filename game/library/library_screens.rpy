## The Library UI, rebuilt after Deadlock's own Library (2024 build).
## Sizes, colours and fonts come from Valve's panorama styles:
##   citadel_db_page_book_library / citadel_ui_library_book (shelf)
##   citadel_db_page_book_toc / citadel_ui_book_nav_button_toc (chapter tree)
##   citadel_tooltip_book_toc (chapter tooltip)
## Fonts and UI images are loaded from the git-ignored game/fonts and
## game/images/ui folders; missing files fall back to Ren'Py defaults.

## ------------------------------------------------------------------
## Colours (citadel_shared_colors)
## ------------------------------------------------------------------

define dl_offwhite = "#FFEFD7"
define dl_offblack = "#10130D"
define dl_green    = "#65951D"   # ritualGreen

## ------------------------------------------------------------------
## Fonts: "serif" = ForevsDemo, "sans" = RetailDemo, body = Reaver.
## The demo fonts only contain letters, digits, space and . , so all
## other characters come from Reaver.
## ------------------------------------------------------------------

init -1 python:

    def dl_ui(name):
        path = "images/ui/%s.png" % name
        return path if renpy.loadable(path) else None

    def dl_thumb(path, size):
        """Crop a 16:9 page to the node / tooltip size."""
        w, h = size
        if not path or not renpy.loadable(path):
            return Solid("#1b1d22", xysize=size)
        sw = int(h * 16 / 9.0)
        if sw >= w:
            return Crop(((sw - w) // 2, 0, w, h), Transform(path, xysize=(sw, h)))
        return Transform(path, fit="cover", xysize=size)

    def dl_book_stats(book):
        unlockable = [c for c in book.chapters if c.parent]
        unlocked = len([c for c in unlockable if book.is_unlocked(c)])
        done, total = book.progress()
        return unlocked, len(unlockable), done, total

    def dl_tree_layout(book, x0=480, dx=240, node=(206, 126), area=(120, 996)):
        """Tidy tree: leaves get evenly spaced rows, parents sit at the mean
        of their children (this reproduces Valve's layout exactly)."""
        kids, roots = {}, []
        for c in book.chapters:
            if c.parent:
                kids.setdefault(c.parent, []).append(c.id)
            else:
                roots.append(c.id)
        rows, depth = {}, {}
        leaves = [0]

        def place(cid, d):
            depth[cid] = d
            ch = kids.get(cid, [])
            if not ch:
                rows[cid] = float(leaves[0])
                leaves[0] += 1
            else:
                rows[cid] = sum(place(k, d + 1) for k in ch) / len(ch)
            return rows[cid]

        for r in roots:
            place(r, 0)
        n = max(leaves[0], 1)
        top, bottom = area
        dy = min(150, (bottom - top - node[1]) / float(max(n - 1, 1)))
        span = (n - 1) * dy + node[1]
        y0 = top + (bottom - top - span) / 2.0
        pos = dict((cid, (int(x0 + depth[cid] * dx), int(y0 + rows[cid] * dy))) for cid in rows)
        return pos, kids

    def dl_branch_finished(book, c):
        """True if the branch starting at chapter c has been played through to
        an ending (some finished chapter in it has no further chapters)."""
        kids = [k for k in book.chapters if k.parent == c.id]
        if not kids:
            return vn_is_complete(book.id, c.id)
        return any(dl_branch_finished(book, k) for k in kids)

    def dl_node_state(book, c):
        if book.is_unlocked(c):
            return "unlocked"
        if c.parent and vn_is_complete(book.id, c.parent):
            # Branches are a choice: once one chapter after this parent has
            # been opened, its siblings stay locked (Unlock All still opens
            # them, like spending extra keys did in Valve's playtest).
            # The lock only lasts for the run in progress: once the chosen
            # branch has been played through to an ending, the other paths
            # open up for the next run.
            for o in book.chapters:
                if (o is not c and o.parent == c.parent and book.is_unlocked(o)
                        and not dl_branch_finished(book, o)):
                    return "unreachable"
            return "unlockable"
        return "unreachable"

## ------------------------------------------------------------------
## Text styles
## ------------------------------------------------------------------

style dl_text is default:
    font DL_BODY
    color dl_offwhite
    size 18

style dl_left_title is dl_text:
    font DL_SERIF
    size 60

style dl_left_text is dl_text:
    size 22
    color "#FFEFD7aa"
    line_spacing 4

style dl_future_title is dl_text:
    font DL_SERIF
    color dl_green
    size 20
    kerning 1

style dl_future_text is dl_text:
    size 18
    color "#FFEFD7aa"
    line_leading 4
    xmaximum 450
    justify True

style dl_available is dl_text:
    font DL_SANS
    size 26
    kerning 1
    color "#FFEFD7b3"

style dl_footer is dl_text:
    size 20

style dl_unlock_progress is dl_text:
    font DL_SEMIBOLD
    italic True
    color "#FFEFD766"

style dl_tip_title is dl_text:
    font DL_BOLD
    size 24
    xalign 0.5
    text_align 0.5

style dl_tip_summary is dl_text:
    size 16
    color "#FFEFD7e6"

style dl_key_label is dl_text:
    font DL_BOLD
    size 16
    color dl_offwhite

style dl_unlock_button is button:
    background Frame(Solid("#ffffff10"), 1, 1)
    hover_background Frame(Solid("#ffffff22"), 1, 1)
    insensitive_background Frame(Solid("#ffffff06"), 1, 1)
    padding (24, 10)

style dl_unlock_button_text is dl_text:
    font DL_SANS
    size 20
    kerning 2
    idle_color "#FFEFD7b3"
    hover_color dl_offwhite
    insensitive_color "#FFEFD740"

style dl_back_label is dl_text:
    font DL_SEMIBOLD
    size 20

## ---- animations ------------------------------------------------

transform dl_fade_up(delay=0.0):
    alpha 0.0 yoffset 30
    pause delay
    ease 0.45 alpha 1.0 yoffset 0

transform dl_fade(delay=0.0, t=0.4):
    alpha 0.0
    pause delay
    ease t alpha 1.0

transform dl_slide_in(delay=0.0):
    alpha 0.0 xoffset -30
    pause delay
    ease 0.4 alpha 1.0 xoffset 0

# shelf card: grow on hover (Valve: scale3D 1.1)
transform dl_card_zoom:
    subpixel True
    xanchor 0.5 yanchor 0.5 xpos 0.5 ypos 0.5
    on idle:
        ease 0.18 zoom 1.0
    on hover:
        ease 0.18 zoom 1.1

# shelf cover: brightness 0.4 -> 1.0 on hover
transform dl_card_cover:
    on idle:
        ease 0.18 matrixcolor TintMatrix("#666666")
    on hover:
        ease 0.18 matrixcolor TintMatrix("#ffffff")

# chapter thumbnail opacity on hover
transform dl_node_thumb(idle_a=0.4, hover_a=1.0):
    on idle:
        ease 0.15 alpha idle_a
    on hover:
        ease 0.15 alpha hover_a

# unlockable chapters pulse (Valve: unlockable_flash, 2s loop)
transform dl_unlock_pulse:
    alpha 0.15
    block:
        ease 1.0 alpha 0.7
        ease 1.0 alpha 0.15
        repeat

# tooltip: quick fade (Valve: 0.1s opacity transition); restarts per chapter
transform dl_tip_in(key=None):
    alpha 0.0 yoffset 6
    ease 0.12 alpha 1.0 yoffset 0

## ------------------------------------------------------------------
## Shared: ESC Back
## ------------------------------------------------------------------

screen dl_back(act):
    key "K_ESCAPE" action act
    button:
        xpos 52 ypos 1010
        background None
        action act
        hbox:
            spacing 12
            frame:
                background Frame(Solid("#5f5f5f"), 4, 4)
                padding (10, 5)
                text "ESC" style "dl_key_label"
            text _("Back") style "dl_back_label" yalign 0.5

## ------------------------------------------------------------------
## The Library (book shelf)
## ------------------------------------------------------------------

screen library():
    tag menu

    add Solid("#000000")
    if dl_ui("library_bg"):
        add Transform(dl_ui("library_bg"), fit="cover", xysize=(1920, 1080), alpha=0.2)

    vbox:
        xpos 60 ypos 80
        xsize 500
        at dl_slide_in(0.0)
        text vn_str("library_title") style "dl_left_title"
        null height 10
        text vn_str("library_desc") style "dl_left_text"
        null height 70
        text vn_str("library_future_label").upper() style "dl_future_title"
        null height 10
        text vn_str("library_future_desc") style "dl_future_text"

        # Valve's text above is from the playtest; say what's different here
        if "library_desc" in VN_STR:
            null height 50
            hbox:
                spacing 14
                add Solid("#65951D") xsize 3 ysize 130
                vbox:
                    spacing 8
                    text _("RESTORATION NOTE") style "dl_future_title" color "#7CBC1D"
                    text _("There are no matches or keys in this restoration: every chapter is free to read, and your choices only change the story.") style "dl_future_text" xmaximum 430

    $ n = len(VN_BOOKS)
    $ cw = 300 if n <= 3 else 255
    $ ch = int(cw * 4 / 3)

    frame:
        xpos 620 ypos 0
        xsize 1200 ysize 1080
        background Solid(dl_offblack + "ee")
        padding (0, 200, 0, 0)

        vbox:
            xfill True
            text vn_str("library_available").upper() style "dl_available" xalign 0.5 at dl_fade(0.1)
            null height 40

            hbox:
                xalign 0.5
                box_wrap True
                for i, book in enumerate(VN_BOOKS):
                    $ done, total = book.progress()
                    $ pct = int(round(100.0 * done / total)) if total else 0
                    button:
                        xsize cw + 40 ysize ch + 100
                        background None
                        action Return(("book", book.id))
                        at dl_fade_up(0.15 + 0.08 * i)
                        fixed:
                            xsize cw ysize ch + 40
                            at dl_card_zoom
                            vbox:
                                add book.cover((cw, ch)) at dl_card_cover
                                frame:
                                    xsize cw ysize 40
                                    background Solid("#666666")
                                    text vn_str("library_progress").replace("[pct_complete]", str(pct)) style "dl_footer" align (0.5, 0.5)

    textbutton _("RESET PROGRESS"):
        style "dl_unlock_button"
        xpos 1780 xanchor 1.0 ypos 1010
        at dl_fade(0.4)
        action Confirm(_("Forget all finished chapters, choices and endings?"), Function(vn_reset_progress))

    use dl_back(Return(("quit",)))

## ------------------------------------------------------------------
## One book: the chapter tree (table of contents)
## ------------------------------------------------------------------

screen book_detail(book):
    tag menu
    default hovered = None

    $ accent = Color(book.accent)
    $ dark = accent.shade(0.28)
    $ pos, kids = dl_tree_layout(book)
    $ unlocked, unlockable, done, total = dl_book_stats(book)
    $ chap = dict((c.id, c) for c in book.chapters)

    # background
    if book.toc_background():
        add Transform(book.toc_background(), fit="cover", xysize=(1920, 1080))
    else:
        add Solid("#0d0f14")
        if dl_ui("library_bg"):
            add Transform(dl_ui("library_bg"), fit="cover", xysize=(1920, 1080), alpha=0.12)

    # title area
    vbox:
        xpos 60 ypos 40
        xsize 440
        at dl_slide_in(0.0)
        if book.logo():
            add book.logo() xalign 0.5
        else:
            text book.title style "dl_left_title" color accent xalign 0.5 text_align 0.5
        null height 20
        text "[unlocked] of [unlockable] Chapters Unlocked" style "dl_unlock_progress" xalign 0.5
        null height 30
        frame:
            xalign 0.5
            background Frame(Solid("#ffffff10"), 1, 1)
            padding (20, 15)
            hbox:
                spacing 20
                frame:
                    xysize (60, 60)
                    background Solid(dl_offblack)
                    padding (0, 0)
                    hbox:
                        align (0.5, 0.5)
                        spacing 4
                        if dl_ui("key"):
                            add dl_ui("key") xysize (22, 22) yalign 0.5 matrixcolor TintMatrix(accent)
                        text "[done]" style "dl_text" font DL_BOLD size 25 color accent yalign 0.5
                vbox:
                    xsize 250
                    text _("Chapters completed:") style "dl_text" font DL_BOLD
                    null height 10
                    frame:
                        xsize 250 ysize 30
                        background Solid("#555555")
                        padding (0, 0)
                        if total:
                            add Solid(accent, xysize=(max(1, int(250 * done / total)), 30))
        null height 16
        textbutton _("UNLOCK ALL CHAPTERS"):
            style "dl_unlock_button"
            xalign 0.5
            sensitive unlocked < unlockable
            action Confirm(_("Unlock every chapter of this book?\nYou can lock them again with Reset progress on the Library shelf."),
                           Function(vn_unlock_all, book.id))

    # connector lines (fade in once the nodes are placed)
    fixed:
      at dl_fade(0.45, 0.5)
      for pid, children in kids.items():
          if pid in pos:
              $ px, py = pos[pid]
              $ cy = [pos[k][1] + 63 for k in children]
              $ sx = pos[children[0]][0] - 20
              $ lc = "#FFEFD740" if book.is_unlocked(chap[pid]) else "#888888"
              add Solid(lc, xysize=(sx - (px + 206), 2)) pos (px + 206, py + 62)
              add Solid(lc, xysize=(2, max(cy + [py + 63]) - min(cy + [py + 63]) + 2)) pos (sx, min(cy + [py + 63]) - 1)
              for k in children:
                  $ kc = "#FFEFD740" if book.is_unlocked(chap[k]) else "#888888"
                  add Solid(kc, xysize=(pos[k][0] - sx, 2)) pos (sx, pos[k][1] + 62)

    # chapter nodes
    for c in book.chapters:
        if c.id in pos and (not c.hidden or book.is_unlocked(c)):
            $ x, y = pos[c.id]
            $ state = dl_node_state(book, c)
            $ hov = hovered == c.id
            $ is_done = vn_is_complete(book.id, c.id)
            if state == "unlocked":
                $ border = accent if hov else accent.replace_opacity(0.19)
            elif state == "unlockable":
                $ border = accent
            else:
                $ border = "#ffffff10"
            $ d = (x - 480) / 240.0
            if state == "unlockable":
                add Solid(accent, xysize=(218, 138)) pos (x - 6, y - 6) at dl_fade(0.1 + 0.09 * d), dl_unlock_pulse
            button:
                pos (x, y)
                xysize (206, 126)
                padding (3, 3)
                at dl_slide_in(0.1 + 0.09 * d)
                background Solid(border)
                hovered SetScreenVariable("hovered", c.id)
                unhovered SetScreenVariable("hovered", None)
                # no key economy in this restoration: a chapter whose parent is
                # finished ("unlockable") opens straight away, same as Valve's
                # unlock-with-a-key but free. Leaving at a chapter-end choice no
                # longer strands the player.
                action (Return(("play", book.id, c.id)) if state in ("unlocked", "unlockable") else NullAction())
                fixed:
                    xysize (200, 120)
                    add Solid("#000000")
                    if state == "unlocked":
                        add dl_thumb(c.thumb, (200, 120)) at dl_node_thumb(0.4, 1.0)
                    elif state == "unlockable":
                        add dl_thumb(c.thumb, (200, 120)) matrixcolor SaturationMatrix(0.0) at dl_node_thumb(0.4, 0.7)
                    else:
                        add dl_thumb(c.thumb, (200, 120)) matrixcolor SaturationMatrix(0.0) alpha 0.15
                    if state != "unlocked" and dl_ui("lock"):
                        # Valve: white lock = can unlock now (.CanAfford), red = can't
                        add dl_ui("lock") xysize (20, 20) align (1.0, 1.0) offset (-10, -10) matrixcolor TintMatrix("#ffffff" if state == "unlockable" else "#ff2a2a")
                    if is_done:
                        frame:
                            xysize (25, 25)
                            xalign 1.0
                            background Solid(accent.replace_opacity(0.6))
                            padding (3, 3)
                            if dl_ui("check"):
                                add dl_ui("check") fit "contain" xysize (19, 19) align (0.5, 0.5) matrixcolor TintMatrix(dl_offblack)

    # tooltip
    if hovered and hovered in pos:
        $ c = chap[hovered]
        $ x, y = pos[hovered]
        $ locked = not book.is_unlocked(c)
        $ tx = x + 216 if x + 216 + 360 < 1900 else x - 370
        $ ty = min(max(20, y - 100), 1080 - 470)
        frame:
            pos (tx, ty)
            xsize 360
            at dl_tip_in(hovered)
            background Solid("#3A0000" if locked else dark)
            padding (20, 10, 20, 14)
            vbox:
                text c.title style "dl_tip_title"
                null height 12
                frame:
                    background Solid("#aaaaaa")
                    padding (1, 1)
                    xalign 0.5
                    add dl_thumb(c.thumb, (318, 179))
                if c.desc:
                    null height 10
                    text c.desc style "dl_tip_summary"
                if locked and dl_ui("lock"):
                    null height 5
                    add dl_ui("lock") xysize (20, 20) xalign 1.0 matrixcolor TintMatrix("#ff2a2a")

    use dl_back(Return(("back",)))
