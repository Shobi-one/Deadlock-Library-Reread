## The four Library books and their chapter graphs.
##
## PLACEHOLDER books, used only until tools/convert.py has generated the real
## ones in game/generated/. The chapter structure below is a PLACEHOLDER. It shows how to express
## branches (a/b paths), merges (any_of) and hidden endings. Once the real
## book data is extracted from an old Deadlock build, replace these lists with
## the actual chapter ids, titles and requirements.

init 0 python:

  if not VN_GENERATED:

      vn_register(VNBook(
          id="geist",
          title="The Binding of Oathkeeper",
          hero="Lady Geist",
          blurb="Lady Geist has to find a way to deal with Oathkeeper.",
          accent="#2f5d50",
          chapters=[
              VNChapter("1",  "Chapter 1", "geist_ch1"),
              VNChapter("2",  "Chapter 2", "geist_ch2", requires=["1"]),
              VNChapter("3a", "Chapter 3a", "geist_ch3a", requires=["2"], flag="geist_path_a"),
              VNChapter("3b", "Chapter 3b", "geist_ch3b", requires=["2"], flag="geist_path_b"),
              VNChapter("4",  "Chapter 4", "geist_ch4", requires=["3a", "3b"], any_of=True),
              VNChapter("5x", "Secret ending", "geist_ch5x", requires=["4"], hidden=True),
          ],
      ))

      vn_register(VNBook(
          id="infernus",
          title="Infernus' Visual Novel",
          hero="Infernus",
          blurb="Infernus has to save Jezebel's, the bar he works at, from being closed.",
          accent="#7a2a1d",
          chapters=[
              VNChapter("1", "Chapter 1", "infernus_ch1"),
          ],
      ))

      vn_register(VNBook(
          id="ivy",
          title="Ivy's Visual Novel",
          hero="Ivy",
          blurb="Ivy wants to get a job to help the Arroyos.",
          accent="#4f6b2c",
          chapters=[
              VNChapter("1", "Chapter 1", "ivy_ch1"),
          ],
      ))

      vn_register(VNBook(
          id="holliday",
          title="Holliday's Visual Novel",
          hero="Holliday",
          blurb="Holliday arrives in New York on the hunt for the Troubadour.",
          accent="#8a5a2b",
          chapters=[
              VNChapter("1", "Chapter 1", "holliday_ch1"),
          ],
      ))
