# FERC Document Trail
#### Grant Project funded by the Fund for Multimedia Documentation
#### of Engaged Learning, The New School.
#### Project supervisor: Stephen Metts

## General Information

The purpose of this project is to assist with extraction of documents submitted to
the Federal Energy Regulatory Commission
([FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp)) and issued by
[FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp).

It serves as a tool for extracting all the documents and meta data relating to
the documents that can be found in
[FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp) online library
available for public access. This application allows passing
a string to the search query (search by some text such as "pipeline") and/or a
docket number that has been assigned to a specific project (or a list of dockets).

The way [FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp) handles
HTML pages is not very friendly for the conventional means of web scraping.
Links are not links, file links don't actually point to the
existing files. Every link generates either a GET or POST HTTP request and such
request is processed by the
[FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp) server.
This scraper does all the HTTP request work by itself and yields traditionally
acceptable output.

## Installation

Clone the repository the regular way of cd'ing into a directory of choice and
issuing the regular git clone command

```
cd Users/username
git clone https://github.com/VzPI/FERC_DOC_TRAIL.git   
cd FERC_DOC_TRAIL
```

This project relies on [Scrapy](https://scrapy.org) platform designed by
[Scrapinghub](https://scrapinghub.com). Scrapy is an advanced tool and it's open
source although credit is due for maintaining such a useful tool.

The only other external library that this project relies on is a library that
was created for [Scrapy](https://scrapy.org) and is called
[scrapy-fake-useragent](https://github.com/alecxe/scrapy-fake-useragent). This
library creates fake headers for requests so that requests look like they are
coming from random browsers.
[FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp) bans high
volume of requests coming in
frequently. The fake browser headers is just one step away from getting banned.
In order to install both libraries type:

```
pip3 install scrapy
pip3 install scrapy-fake-useragent
```

## Setup
Before starting the project - open the repository folder that you cloned and go
to the **FERC** folder that contains the **spiders** folder. Open the
**fercgov.py**
file with a text editor and go to line 36 for general info and description.
After reading the description navigate to lines **108** and **111** - your search
parameters are there. The docket parameter **HAS** to be a list even if it has one
or zero dockets (empty list). Respectively, variable **search** has to be a
string, current version of this project doesn't support a list of strings since
it mimics the basic functionality of
[FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp) search form. Please
don't leave both the search field and docket list empty. Although the
[FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp) search engine will
allow accessing all the existing documents that way, current version of this application's
file tree builder doesn't support this functionality yet. It's quite a niche need
and it might be added in the future.

Make sure that the search parameters are the ones that you need (for the
project(s) that you're inquiring about).

The **settings** file in the FERC directory has the setting:
``` python
DOWNLOAD_DELAY = 2
```
By default this project is ethical towards the
[FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp) servers - 2
seconds is a good enough delay that shouldn't cause
the servers to go down and consume much of processing power by overloading.
[Scrapy](https://scrapy.org) will take this number and request pages at a delay
that ranges from 0.5 - 1.5 times the delay value (i.e. 1.2 * 2 = 2.4 seconds).
This way you are not bombarding the server with several hundred requests per minute
. You can manually change it to higher or lower value (down to 0) depending on your
project. **This setting is your responsibility**, consider yourself warned.

## Launch
Assuming you followed all the above instructions and everything worked correctly -
all required libraries have been installed and you're in the repository directory.
Now you can issue the following command in the terminal:

```
scrapy crawl fercgov
```
fercgov is the name of the spider that is used to send requests and record the
activity + download files. It is different from the regular structure of
[Scrapy](https://scrapy.org) project where the item is generated and passed
through a pipeline. This is due to the fact that an item is populated across
multiple nodes that are traversed via new requests (data from previous pages is
passed to such requests), in addition the regular
[Scrapy](https://scrapy.org) file download pipelines don't work - the file links
are internal links to be processed by the server, they don't actually point to
files directly.

## Downloaded files and log.json
The script writes its output to a **log.json** located in the
**FERC_DOC_TRAIL/FERC/download_folder**
directory. It saves all the documents in the same directory, so that all the output
is conveniently located in that folder.

## Convert to CSV
JSON was intentionally used as one of the easiest wide-spread formats
to use (requires no database setup and is easily parsable with python when we
need to determine whether entries exist) however one may prefer to work with CSV
since it's readable by Excel and is preferable in the office environment. To
duplicate the log file run the following commands:
```
cd FERC
python3 process_to_csv.py
```
If you just ran the main spider script - you're already in **FERC_DOC_TRAIL** directory
therefore you **cd** only once again (as noted in the code above) to get to
**FERC_DOC_TRAIL/FERC**

## Rerunning the scraper
If the scraper was interrupted for some reason due to an error (the server was down)
or interrupted by the user (press **CTRL+C** twice to force it to stop immediately),
feel free to run the following command again:
```
scrapy crawl fercgov
```

The file is only recorded in the log when it's downloaded - if you skipped a file
due to an error, the file will be downloaded if you restart the scraper. The CSV
file needs to be recreated every time the scraper adds new files (since only the
  log.json file is updated).

This applies to rerunning the scraper in order to gather new documents. Running the
crawl command will get all the new files.


## Errors and output
* The longest we ran the scraper for is **7 hours** with the search for all library
entries that contain the word **"pipeline"** - we terminated it when it downloaded
**~8.77 Gb**. We were downloading with a **1 second** delay. All this conditions didn't
get us banned, your results may vary.
* The most common error that we saw was related to file names, therefore some files
weren't downloaded. There were about a dozen of such cases (maybe 20 at most) which
is acceptable for 8 Gb of files yet doesn't seem satisfactory for our perfectionism.
These errors will be examined in the future, for now they are accompanied with the following
error messages that you will see in the terminal. They return the file url so you can
download it manually until the problem is resolved. We addressed most of the variation
issues that we encountered in the library (i.e. flexible columns in json file which
get created whenever there is a new file format discovered) yet this is the example where
flexibility is desirable but not achieved easily - we have to extract the format of the
file from the server so that we can actually open the downloaded file.

```
{'=============FILENAME ERROR=============': 'https://elibrary.ferc.gov/idmws/common/FN_error.asp?flag=5&fileNetID=32387352&pageNumber='}
```
Alternatively:
```
{'=============FORMAT ERROR=============': '###############################'}
```
In our experience (even though we didn't actually do the proper analysis of this issue)
the frequency of such errors was much higher with lower delays - it is likely that
the server is struggling to handle a large volume of requests.

## Miscellaneous recommendations
* Do not launch the scraper on weekends. I think someone physically turns off
the server - no request returns any response
* [FERC](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp) bans for some
noticeable time. There are only two reasons for the scraper not working: you got banned or
the server is down (for the weekend or temporarily). When you get banned your script
either produces errors constantly or terminates early. The easiest way to confirm that you are
banned is to open [this link](https://elibrary.ferc.gov/idmws/search/fercgensearch.asp)
and click **submit**. If you get the following page in response:


![ban image](https://i.imgur.com/3aiNZJb.jpg "ban image")


We recommend to wait for some time - a day or two is quite a consistent time but
there were cases when we were unbanned in less than a day after some aggressive
testing (where the image comes from).
You may also see the following page:


![down image](https://i.imgur.com/AjHdNRQ.png "down image")


This usually indicates of the server being down - check again in 10 minutes.


  * Think about your requests in advance - if you play with the scraper for too
long and get banned you will have to wait for the ban to go down. Use it only
for the requess that you are sure about (tested docket numbers, proper search
strings etc.)


## Legal
* Scraping is legal
* Scrape responsibly and respectfully - if you actually end up costing a significant amount of money
for server processing time you can be liable for the damages. Getting cease and desist letters
is a potential scenario and they are much better than compensating for the damages.
* Our default download delay is set to **3 seconds** - this will yield more than a half a GB
of documents in an hour. That's half a GB of PDF files, DOC files and images. It isn't
likely that you're going to process all the documents in a day, don't bee greedy
and opt in for longer or default delay, be realistic and respectful.



P.S. We will be updating this section later - it takes time to remember all the
details
