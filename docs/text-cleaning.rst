Preparing texts for CLiCTagger
******************************

Whilst CLiCTagger can work on any plain text, for best results text should be prepared using the method below.
Any texts added to the `corpora repository <https://github.com/mahlberg-lab/corpora>`__ should follow this process.

To clean texts so they are ready for use with CLiCTagger, the following steps need to be followed.

1. `Save as/convert to UTF-8 and use typographical ('curly') quote marks`_.

2. `Convert to unix line endings`_.

3. `Remove non-authorial text`_.

4. `Reformat the book title and author to make consistent across all texts`_.

5. `Reformat chapter headings to make consistent across all texts`_.

6. `Manual corrections`_.

If committing to the corpora repository, each editing stage is committed and clearly documented with a commit message.
Accordingly, it is possible to see the history of a single file, see for example the `history of willows.txt <https://github.com/mahlberg-lab/corpora/commits/master/ChiLit/willows.txt>`__.

Save as/convert to UTF-8 and use typographical ('curly') quote marks
-----------------------------------------------------------------------

The CLiC Tagger expects files in UTF-8. Ideally, typographical ('curly') quote marks should be used to avoid confusion between quote marks and apostrophes.

Convert to unix line endings
----------------------------

Step [2] is achieved using the following command::

     for f in ChiLit/*.txt; do dos2unix -m $f; done 

Remove non-authorial text
-------------------------

-   Tables of content are removed.
-   Lists of illustrations are removed.
-   Any preface text attributed to a person other than the author is
    removed. When attribution is unclear the text is left.
-   Any postface text attributed to a person other than the author is
    removed. When attribution is unclear the text is left.
-   Transcriber notes are removed.
-   In the texts illustrations are usually indicated by text enclosed in
    square brackets. Where this text includes a caption the caption is
    kept, for example::

         [Illustration: THE WONDERSTONE.] 

    becomes::

         [THE WONDERSTONE.] 

    Where there is no authorial caption the construct is deleted. All
    the following example would be deleted::

         [Illustration] 

         [Illustration: Chapter Seventeen] 

         [Illustration: Page 91]
        
    In the case of `sketches`, the line::
    
          [Picture which cannot be reproduced]

    was removed during editing, because other editions suggested that the line was 
    not part of the text but rather an editorial remark (see the `comment on the change <https://github.com/mahlberg-lab/corpora/commit/c72cc1809c22c3f45f2e3158df87545fdce58d28#r32025083>`__).
    
-  **Footnotes** are removed if they are attached to the end of a text but left in if the footnote text
   is included in main text. (This rule was formally introduced for the `expansion of the ArTs corpus, 2019-01 <https://github.com/mahlberg-lab/corpora/commit/c72cc1809c22c3f45f2e3158df87545fdce58d28#diff-b90e831a9520a85b9e7620aa1fac6591L25366>`__, although it was likely also followed implicitly for the previous corpora).
   When removing footnotes, delete both the in-text footnote indicator and the footnote itself.
   In the following example from `sketches`, the {161} in the text `was removed <https://github.com/mahlberg-lab/corpora/commit/c72cc1809c22c3f45f2e3158df87545fdce58d28#diff-b90e831a9520a85b9e7620aa1fac6591L7281>`__::
   
        On both sides of the gaol, is a small
        receiving-room, to which prisoners are conducted on their first
        reception, and whence they cannot be removed until they have been
        examined by the surgeon of the prison. {161}
    
   `along with the footnote text <https://github.com/mahlberg-lab/corpora/commit/c72cc1809c22c3f45f2e3158df87545fdce58d28#diff-b90e831a9520a85b9e7620aa1fac6591L26670>`__::
   
        {161}  The regulations of the prison relative to the confinement of
        prisoners during the day, their sleeping at night, their taking their
        meals, and other matters of gaol economy, have been all altered-greatly
        for the better—since this sketch was first published.  Even the
        construction of the prison itself has been changed.
        
   Note this is just one of the `four footnotes removed in "sketches" <https://github.com/mahlberg-lab/corpora/commit/c72cc1809c22c3f45f2e3158df87545fdce58d28#diff-b90e831a9520a85b9e7620aa1fac6591L26663>`__. 
   Other books for which footnotes were removed include `"americannotes" <https://github.com/mahlberg-lab/corpora/commit/c72cc1809c22c3f45f2e3158df87545fdce58d28#diff-97c35dfce2b9f9b909ebb3f89ae43e2c>`__, 
   `"pictures" <https://github.com/mahlberg-lab/corpora/commit/c72cc1809c22c3f45f2e3158df87545fdce58d28#diff-dae9e8214d88284bc935c3a2b5ebce82>`__ and `"uncommercial" <https://github.com/mahlberg-lab/corpora/commit/c72cc1809c22c3f45f2e3158df87545fdce58d28#diff-f573870f5118cfc91ff22ca3de87a75f>`__.
   
   By contrast, an example of a footnote that was retained because it was fully included
   in the main text is the following in `"timemachine" <https://github.com/mahlberg-lab/corpora/blob/ca01d2ae9731b7a43d469422b85deb0bc1c486f3/ArTs/timemachine.txt#L2231>`__::
   
       “Suddenly Weena came very close to my side. So suddenly that she
       startled me. Had it not been for her I do not think I should have
       noticed that the floor of the gallery sloped at all. [Footnote: It may
       be, of course, that the floor did not slope, but that the museum was
       built into the side of a hill.—ED.]
       
   ChiLit also contains examples of retained footnotes, for example several in *rival*,
   such as the following (`see location in text <https://github.com/mahlberg-lab/corpora/blob/ca01d2ae9731b7a43d469422b85deb0bc1c486f3/ChiLit/rival.txt#L2504>`__)::
   
       "By the mercy of Heaven, we met some Brazilian proas, which took us on
       board, and the Diomede in tow; and, having favourable winds and a smooth
       sea, we contrived to get the hulk into the King's dock at Rio de
       Janeiro; where, being a fine new ship, she was found worth repairing and
       refitting; and here we have been ever since, the Portuguese workmen
       being very slow in their operations."[6]

       [Footnote 6: Commodore Byron found some repairs necessary at Rio de
       Janeiro.--"We had six Portuguese caulkers to assist our carpenters, who
       were paid at the rate of 6s. per diem; though it is certain an English
       caulker could do as much in one day as they did in three; but, though
       slow and inactive, they perform their work very effectually."

Reformat the book title and author to make consistent across all texts
----------------------------------------------------------------------
       
-   The **book title** is put on the first line of the file, without any
    newlines.
-   The **book author** is put on the second line of the file, without any
    newlines. Check whether the CLiC corpora already contain other texts from this author
    and ensure that the spelling of the name is consistent in the text to be added. 
    If the presentation of the name differs slightly (e.g. a full name vs. initials of first name)
    then CLiC will consider the two names as different authors and give them distinct author entries
    in the dropdown menu. Sometimes Gutenberg texts also contain additional titles in front of a name
    (e.g. "Baron", "Captain", "Earl"). We try to use the format that is/was most commonly used for the 
    author. Most important is, though, to use one format consistently for the same author.
-   Both the **book title** and the **book author** should be in title case
    (*not* in all capitals! - that would confuse the CLiC client), for example::

          American Notes for General Circulation
          Charles Dickens

Reformat chapter headings to make consistent across all texts
-------------------------------------------------------------

-   **Chapter headings** are formatted as follows: If the chapter heading
    begins with 'CHAPTER' or 'BOOK' it must be followed by a number or
    roman numerals and then a dot. The chapter or book number cannot be
    written in word form. The heading can optionaly be followed by a
    chapter title; the chapter title must not break onto a new line.
    Here are some examples::

         CHAPTER 1. The Old Sea-dog at the Admiral Benbow

         CHAPTER 2. TRAVELLING COMPANIONS.

         CHAPTER 3.

         CHAPTER IV. Little Meg's Treat to Her Children

         CHAPTER V.

         BOOK 1.

         BOOK II. Jessica's Mother

    Sections beginning with 'INTRODUCTION', 'PREFACE', 'CONCLUSION',
    'PROLOGUE', 'PRELUDE' or 'MORAL' are also be treated as seperate
    chapters. These do not require numbers, but do require the dot.
    Again the heading can optionaly be followed by a title; the title
    must not break onto a new line. Here are some examples::

         PREFACE.

         INTRODUCTION.

         PROLOGUE. THE OLYMPIANS

         MORAL.--_There is no moral to this chapter._

    In all cases there must be no space at the beginning of the line.

-   **Part headings** are on a line before the first chapter of that part,
    in the same format (i.e. "PART" has to be followed by a Roman or Arabic
    numeral). Blank lines are allowed between the part heading and the chapter
    heading. The following example is from `treasure`::
    

        PART 2. The Sea-cook




        CHAPTER 7. I Go to Bristol

        IT was longer than the squire imagined ere we were ready for the sea,
        and none of our first plans--not even Dr. Livesey's, of keeping me
        
    In the CLiC dropdown menu, the part and chapter headings are joined together,
    i.e. this `treasure` chapter is shown as "PART 2. The Sea-cook CHAPTER 7. I Go to Bristol".
    Whereas `treasure` contains "PART" headings in the original text that only had to
    be `reformatted <https://github.com/mahlberg-lab/corpora/commit/b3bf771a72a523554fbec011dfaf6e44d35b1ae8#diff-833d382b4e9e60c1c7f9182dd7ebd234>`__, sometimes "PART" (and a number) has to be added
    to the existing headings in order to represent the structure of the book correctly
    in the CLiC dropdown menu. An example where the headings had to be adjusted accordingly 
    is `sketches`. The table of contents in a `scanned copy of the book <https://archive.org/details/in.ernet.dli.2015.501383/page/n7>`__
    illustrates its nested structure. This table of contents does not reproduce all levels;
    for example, the chapters within "CHARACTERS" and "TALES" contain a further level of chapters.
    As CLiC can only handle parts and chapters but no third level, we solved this issue by first adding
    the numbered parts to the headings ("PART 4." in the following), joining it with the top
    chapter level ("CHAPTER I. THE BOARDING-HOUSE") and therefore accounting for the extra chapter level (CHAPTER I.)
    on level 2::
    
    
         PART 4. TALES CHAPTER I. THE BOARDING-HOUSE


          CHAPTER I.
          
    These extra levels are not very frequent in `sketches`, but when they occur, they are not
    necessarily numbered conventionally but e.g. "CHAPTER THE SECOND". In that instance, we added
    only "CHAPTER" to count this as a chapter::
    
         The advertisement has again appeared in the morning papers.  Results must
         be reserved for another chapter.


         CHAPTER. CHAPTER THE SECOND.


         ‘Well!’ said little Mrs. Tibbs to herself, as she sat in the front
         parlour of the Coram-street mansion one morning, mending a piece of
         stair-carpet off the first Landings;—‘Things have not turned out so
         badly, either, and if I only get a favourable answer to the
         advertisement, we shall be full again.’

Manual corrections
------------------

When previewing the output of the CLiC tagger output, you might notice that manual corrections are necessary. These could relate to correcting the format to properly follow the steps listed above, or might point to instances of, for example, missing quote marks. See `this example <https://github.com/mahlberg-lab/corpora/commit/e452aa520a8503df63b1628d5863e4c3c2f6f4da#diff-151a8e57bf7163871654b38b87fc1444f677d617882e10297abe2f700862303e>`_ of a manual correction (adding a missing closing quote mark) in the CLiC ArTs corpus.
