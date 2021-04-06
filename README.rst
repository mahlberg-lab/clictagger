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

Windows / MacOS
---------------

Under either you can install clictagger via. `Anaconda <https://docs.conda.io/projects/conda/en/latest/user-guide/index.html>`__:

1. Install `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__ if you haven't already.
2. Start an `Anaconda prompt <https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html>`__
3. ``conda create --name clictagger icu pyicu git pip``
4. ``conda activate clictagger``
5. ``pip install git+https://github.com/birmingham-ccr/clictagger``

Usage
=====

Python notebook
---------------

See the example notebook here: https://mybinder.org/v2/gh/birmingham-ccr/clictagger/HEAD?filepath=getting_started.ipynb

Command line
------------

.. image:: commandline_example.svg
    :align: center
    :alt: Animation of command_line usage

You should now have the ``clictagger`` command available. See ``--help`` for usage.
Some examples follow.

To see the contents of ``alice.txt`` with regions coloured::

    clictagger alice.txt

Output all suspensions in ``alice.txt`` into ``alice.csv``::

    clictagger --csv alice.csv alice.txt quote.suspension.short quote.suspension.long

Start a webserver to view the contents of ``alice.txt`` with regions coloured.
Whenever the page is reloaded, ``alice.txt`` will be re-read::

    clictagger --serve alice.txt
