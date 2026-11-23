## Speakers and their sprites.
## Sprites use placeholders until a PNG exists at the given path.
## Add expressions as new image lines, e.g.
##     image geist angry = vn_sprite("images/books/geist/geist_angry.png", "#2f5d50", "Lady Geist (angry)")

define narrator = Character(None, what_italic=False)

define geist    = Character("Lady Geist", color="#7fc4a8")
define infernus = Character("Infernus",   color="#e0704f")
define ivy      = Character("Ivy",        color="#a8c46a")
define holliday = Character("Holliday",   color="#e0a860")

image geist    = vn_sprite("images/books/geist/geist.png",       "#2f5d50", "Lady Geist")
image infernus = vn_sprite("images/books/infernus/infernus.png", "#7a2a1d", "Infernus")
image ivy      = vn_sprite("images/books/ivy/ivy.png",           "#4f6b2c", "Ivy")
image holliday = vn_sprite("images/books/holliday/holliday.png", "#8a5a2b", "Holliday")

image bg placeholder = vn_bg("images/bg_placeholder.png", "Background")
