Creating projects and building corpora
=======================================

Doing corpus linguistics involves building and interrogating corpora, and exploring interrogation results. ``corpkit`` helps with all of these things. This page will explain how to create a new project and build a corpus.

.. contents::
   :local:

Creating a new project
-----------------------

The simplest way to begin using corpkit is to import it and to create a new project. Projects are simply folders containing subfolders where corpora, saved results, images and dictionaries will be stored. The simplest way is to do it is to use the ``new_project`` command in `bash`, passing in the name you'd like for the project as the only argument:

.. code-block:: bash

   $ new_project psyc
   # move there:
   $ cd psyc
   # now, enter python and begin ...

Or, from Python:

.. code-block:: python

   >>> import corpkit
   >>> corpkit.new_project('psyc')
   ### move there:
   >>> import os
   >>> os.chdir('psyc')
   >>> os.listdir('.')
   
   ['data',
    'dictionaries',
    'exported',
    'images',
    'logs',
    'saved_concordances',
    'saved_interrogations']

Adding a corpus
----------------

Now that we have a project, we need to add some plain-text data to the `data` folder. At the very least, this is simply a text file. Better than this is a folder containing a number of text files. Best, however, is a folder containing subfolders, with each subfolder containing one or more text files. These subfolders represent subcorpora. 

You can add your corpus to the `data` folder from the command line, or using Finder/Explorer if you prefer.

.. code-block:: bash

   $ cp -R /Users/me/Documents/transcripts ./data

Or, in `Python`, using `shutil`:

.. code-block:: python

   >>> import shutil
   >>> shutil.copytree('/Users/me/Documents/transcripts', './data')

If you've been using `bash` so far, this is the moment when you'd enter `Python` and ``import corpkit``.

Creating a Corpus object
-------------------------

Once we have a corpus of text files, we need to turn it into a `Corpus` object.

.. code-block:: python

   >>> from corpkit import Corpus
   ### you can leave out the 'data' if it's in there
   >>> unparsed = Corpus('data/transcripts')
   >>> unparsed
   <corpkit.corpus.Corpus instance: transcripts; 13 subcorpora>



Pre-processing the data
----------------------------------

A `Corpus` object can only be interrogated if tokenisation or parsing has been performed. For this, :class:`corpkit.corpus.Corpus` objects have :func:`~corpkit.corpus.Corpus.tokenise` and :func:`~corpkit.corpus.Corpus.parse` methods. Tokenising is faster, simpler, and will work for more languages. As shown below, you can also elect to POS tag and lemmatise the data:

.. code-block:: python

   > corpus = unparsed.tokenise(postags=True, lemmatisation=True)
   # switch either to false to disable---but lemmatisation requires pos

Parsing relies on Stanford CoreNLP's parser, and therefore, you must have the parser and Java installed. ``corpkit`` will look around in your PATH for the parser, but you can also pass in its location manually with (e.g.) ``corenlppath='users/you/corenlp'``. If it can't be found, you'll be asked if you want to download and install it automatically. Parsing has sensible defaults, and can be run with:

.. code-block:: python

   >>> corpus = unparsed.parse()

.. note::

    Remember that parsing is a computationally intensive task, and can take a long time!

``corpkit`` can also work with speaker IDs. If lines in your file contain capitalised alphanumeric names, followed by a colon (as per the example below), these IDs can be stripped out and turned into metadata features in the parsed dataset.

.. code-block:: none

    JOHN: Why did they change the signs above all the bins?
    SPEAKER23: I know why. But I'm not telling.

To use this option, use the ``speaker_segmentation`` keyword argument:

.. code-block:: python

   >>> corpus = unparsed.parse(speaker_segmentation=True)

Tokenising or parsing creates a corpus that is structurally identical to the original, but with annotations in `CONLL-U` formatted files in place of the original ``.txt`` files. When parsing, there are also methods for multiprocessing, memory allocation and so on:

+--------------------------+------------+---------------------------------------+
| `parse()` argument       | Type       | Purpose                               |
+==========================+============+=======================================+
| `corenlppath`            | `str`      | Path to CoreNLP                       |
+--------------------------+------------+---------------------------------------+
+--------------------------+------------+---------------------------------------+
| `operations`             | `str`      | `List of annotations`_                |
+--------------------------+------------+---------------------------------------+
| `copula_head`            | `bool`     | Make copula head of dependency parse  |
+--------------------------+------------+---------------------------------------+
| `speaker_segmentation`   | `bool`     | Do speaker segmentation               |
+--------------------------+------------+---------------------------------------+
| `memory_mb`              | `int`      | Amount of memory to allocate          |
+--------------------------+------------+---------------------------------------+
| `multiprocess`           | `int/bool` | Process in `n` parallel jobs          |
+--------------------------+------------+---------------------------------------+
| `outname`                | `str`      | Custom name for parsed corpus         |
+--------------------------+------------+---------------------------------------+

You can run parsing operations from the command line:

.. code-block:: bash

   $ parse mycorpus --multiprocess 4 --outname MyData

Manipulating a parsed corpus
-----------------------------

Once you have a parsed corpus, you're ready to analyse it. :class:`corpkit.corpus.Corpus` objects can be navigated in a number of ways. *CoreNLP XML* is used to navigte the internal structure of `CONLL-U` files within the corpus.

.. code-block:: python

   >>> corpus[:3]                             # access first three subcorpora
   >>> corpus.subcorpora.chapter1             # access subcorpus called chapter1
   >>> f = corpus[5][20]                      # access 21st file in 6th subcorpus
   >>> f.document.sentences[0].parse_string   # get parse tree for first sentence
   >>> f.document.sentences.tokens[0].word    # get first word


Counting key features
-----------------------

Before constructing your own queries, you may want to use some predefined attributes for counting key features in the corpus. 

.. code-block:: python

   >>> corpus.features

Output: 

.. code-block:: none

   S   Characters   Tokens    Words  Closed class  Open class  Clauses  Sentences  Unmod. declarative  Passives  Mental processes  Relational processes  Mod. declarative  Interrogative  Verbal processes  Imperative  Open interrogative  Closed interrogative  
   01     4380658  1258606  1092113        643779      614827   277103      68267               35981     16842             11570                 11082              3691           5012              2962         615                 787                   813  
   02     3185042   922243   800046        471883      450360   209448      51575               26149     10324              8952                  8407              3103           3407              2578         540                 547                   461  
   03     3157277   917822   795517        471578      446244   209990      51860               26383      9711              9163                  8590              3438           3392              2572         583                 556                   452  
   04     3261922   948272   820193        486065      462207   216739      53995               27073      9697              9553                  9037              3770           3702              2665         652                 669                   530  
   05     3164919   921098   796430        473446      447652   210165      52227               26137      9543              8958                  8663              3622           3523              2738         633                 571                   467  
   06     3187420   928350   797652        480843      447507   209895      52171               25096      8917              9011                  8820              3913           3637              2722         686                 553                   480  
   07     3080956   900110   771319        466254      433856   202868      50071               24077      8618              8616                  8547              3623           3343              2676         615                 515                   434  
   08     3356241   972652   833135        502913      469739   218382      52637               25285      9921              9230                  9562              3963           3497              2831         692                 603                   442  
   09     2908221   840803   725108        434839      405964   191851      47050               21807      8354              8413                  8720              3876           3147              2582         675                 554                   455  
   10     2868652   815101   708918        421403      393698   185677      43474               20763      8640              8067                  8947              4333           3181              2727         584                 596                   424

This can take a while, as it counts a number of complex features. Once it's done, however, it saves automatically, so you don't need to do it again. There are also ``postags``, ``wordclasses`` and ``lexicon`` attributes, which behave similarly:

.. code-block:: python

   >>> corpus.postags
   >>> corpus.wordclasses
   >>> corpus.lexicon

These results can be useful when generating relative frequencies later on. Right now, however, you're probably interested in searching the corpus yourself, however. Hit `Next` to learn about that.

.. _List of annotations: http://nlp.stanford.edu/index.shtml
