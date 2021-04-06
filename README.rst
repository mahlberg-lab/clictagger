CLiCTagger Region-tagging
*************************

Python module to identify regions in text.

Part of the `CLiC project <https://www.birmingham.ac.uk/schools/edacs/departments/englishlanguage/research/projects/clic/index.aspx>`__

Installation
============

Linux
-----

First make sure you have the following prerequisites installed::

    apt-get install python3 python3-dev \
        libicu-dev pkg-config

Then install via. pip::

    pip install git+https://github.com/birmingham-ccr/clictagger

Usage
=====

Python notebook
---------------

See the example notebook here: https://mybinder.org/v2/gh/birmingham-ccr/clictagger/HEAD?filepath=getting_started.ipynb

Command line
------------

![Animation of command_line usage](commandline_example.svg)

You should now have the ``clictagger`` command available. See ``--help`` for usage.
Some examples follow.

To see the contents of ``alice.txt`` with regions coloured::

    clictagger alice.txt

Output all suspensions in ``alice.txt`` into ``alice.csv``::

    clictagger --csv alice.csv alice.txt quote.suspension.short quote.suspension.long

Start a webserver to view the contents of ``alice.txt`` with regions coloured.
Whenever the page is reloaded, ``alice.txt`` will be re-read::

    clictagger --serve alice.txt
