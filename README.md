24pullrequests-stats
====================

It is a messy code to generate stats about `24pullrequests`, some insights about it are in http://notenoughmemory.com/2013/01/24pullrequests-post-mortem.html.

Do not expect a good code or something easy to use. I know it loads a lot of data to memory and probably will crash if I try to do it with more data.

I used ~400MB of data, so it is not easy to upload it to GitHub, even compressed. Download data from https://s3.amazonaws.com/notenoughmemory/24pullrequests-stats.zip and unzip in data folder, so you can use my code without download everything again with `downloader.py`.

If you want to use this code, check the `stats.py` file. After these scripts, I did some parsing and created graphics with Google Spreadsheets.
