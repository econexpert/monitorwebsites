# Monitor websites

Check for website updates and store data in MongoDb database using Python script.

Need MongoDb account with read/write user login access and pymongo package installed locally to run the script. 

## 1. Check for website changes and record size in database
File name: *monitorweb.py*

![](https://github.com/econexpert/monitorwebsites/blob/main/images/monitorchanges.jpg)

Database entries: 

![](https://github.com/econexpert/monitorwebsites/blob/main/images/testme-database.jpg)

## 2. Check for websites changes and save HTML copy in database

File name: *monitorweb02.py*

If detects changes, this version saves copy of HTML on MongoDb and makes an archive of earlier versions.   

Need MongoDb account with read/write user login access and pymongo package installed locally to run the script. 

![](https://github.com/econexpert/monitorwebsites/blob/main/images/monitorchanges02.jpg)

## 3. Retrieve saved copies and analyze for changes
File name: *monitorweb02-readcomperehtml.py*

This file uses database entries created by monitorweb02.py and compare last saved html file with the previous one. Shows added and removed lines. 

Still work in progress. Not working on scripted and encoded pages. 

![](https://github.com/econexpert/monitorwebsites/blob/main/images/monitor02readweb.jpg)
