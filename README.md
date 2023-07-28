# Monitor websites

Check for website updates and store data in MongoDb database using Python script.

Need MongoDb account with read/write user login access and pymongo package installed locally to run the script. 

Here are the steps involved in using these scripts:

1. Download and save the .py files (go to the script and click on 'Download raw file').
2. Create a MongoDB account with a strong and secure password (visit https://www.mongodb.com/).
3. Create MongoDB users and obtain the connection string (refer to the video tutorial).

https://github.com/econexpert/monitorwebsites/assets/7473991/9cf6641e-152c-4ea3-9188-3bfaf2f518e2

4. Update the connection string inside the Python scripts.
5. Install pymongo pckage: ```pip3 install pymongo``` or ```python -m pip install pymongo```
6. Run the scripts in the terminal. For example: python3 monitorweb02.py


## 1. Check for website changes and record size in database
File name: *monitorweb.py*


This version saves size of website in database if it detects changes. Can be used to alert user about updates.
![](https://github.com/econexpert/monitorwebsites/blob/main/images/monitorchanges.jpg)

Database entries: 

![](https://github.com/econexpert/monitorwebsites/blob/main/images/testme-database.jpg)

More updated version follows.    

## 2. Check for websites changes and save HTML copy in database

File name: *monitorweb02.py*

This script saves HTML file copy of the website on MongoDb database, if it detects changes. All earlier versions of websites are stored in the database.  

Database settings and saved in the file settings.py

Need MongoDb account with read/write user login access and pymongo package installed locally to run the script. 

![](https://github.com/econexpert/monitorwebsites/blob/main/images/monitorchanges02.jpg)

## 3. Retrieve saved copies and analyze for changes
File name: *monitorweb02-readcomperehtml.py*

This file uses database entries created by monitorweb02.py and compare last saved html file with the previous one. Shows added and removed lines. 

Still work in progress. Not working on scripted and encoded pages. 

![](https://github.com/econexpert/monitorwebsites/blob/main/images/monitor02readweb.jpg)

## 4. Prepare html file or email summary about updates 
File name: *monitorweb04-summary.py*

This file can be used to email daily summaries about updates or just save html file with information. Most convenient way is to upload to a free public notebook service for daily run. Number of days to summarize can be set main function. If number of days set as 0 days, menu is displayed to input number of days.   

Example of e-mail summary is attached below.     

![](https://github.com/econexpert/monitorwebsites/blob/main/images/monitorweb04-summary.jpg)

