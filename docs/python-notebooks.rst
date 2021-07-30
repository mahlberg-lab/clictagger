Running CLiCTagger online via a Python notebook
************************************************

You can run CLiCTagger online via a Python notebook. There are currently two notebooks:

1. The `getting_started.ipynb notebook <https://mybinder.org/v2/gh/mahlberg-lab/clictagger/HEAD?filepath=getting_started.ipynb>`__: this notebook allows you to load text from a) a string (i.e. copy and paste), b). the `corpora repository <https://github.com/mahlberg-lab/corpora>`_, or c) your own (online) repository

2. The `file-upload.ipynb notebook <https://mybinder.org/v2/gh/mahlberg-lab/clictagger/HEAD?filepath=file-upload.ipynb>`__: this notebook allows you to upload files from your computer

How to run the notebooks
========================

To load text and run the tagger on your text, you need to run the code in the various cells. This has to be done in sequence. So, we recommend re-running all cells every time you make a change; go to "Cell" in the menue and select "Run all".

"Dead kernel" error message
===========================

When you return to the Python notebook after a period of absence, you may find the following message:

         The kernel has died, and the automatic restart has failed. It is possible the kernel cannot be restarted. If you are not able to restart the kernel, you will still be able to save the notebook, but running code will no longer work until the notebook is reopened.

Choose "Try Restarting Now" and, when it has reloaded, click "Cells" -> "Run all".
