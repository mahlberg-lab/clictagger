Importing CLiCTagger CSVs into Excel
************************************

CLiCtagger CSVs are encoded as `UTF-8 <https://en.wikipedia.org/wiki/UTF-8>`__,
so all characters from source texts, e.g. curly quotes, can be represented.

To import these into Excel, you need to tell it to use UTF-8 when reading CSVs.
This varies depending on the version of Excel you are using.

Excel for Windows
=================

You need to use `Power Query <https://support.microsoft.com/en-us/office/import-data-from-external-data-sources-power-query-be4330b3-5356-486c-a168-b68e9e616f5a>`__:

1. Open a new Excel file
2. Open the “Data” tab
3. In the “Get Data” menu on the left, click on “From Text/CSV”
4. Select a file in the explorer
5. Click “Import”
6. Under "File origin", choose "65001: Unicode (UTF-8)"
7. Under “Delimiter”, choose “Comma”
8. Click ”Load”
9. Save file

Excel for Mac
=============

You need to use the `File / Import menu <https://support.microsoft.com/en-us/office/import-data-from-a-csv-html-or-text-file-b62efe49-4d5b-4429-b788-e1211b5e90f6>`__:

1. Click "File"
2. Click "Import"
3. Choose  "CSV file"
4. Select a file in the finder
5. Click "Get Data"
6. In the Text Wizard, choose "Delimited"
7. Choose "File origin" "Unicode (UTF-8)"
8. Click "Next"
9. Under "Delimiters", choose "Comma"
10. Click "Next"
11. Under "Column data format", choose "General" (I think)
12. Click "Finish"
13. Save file
