from pymongo import MongoClient
from sys import exit
import bz2
import datetime
import settings

def gettitle(pagehtml,first,second):
    title = pagehtml[pagehtml.find(first) + len(first): pagehtml.find(second, pagehtml.find(first) + 1)]
    return title

def removecodes(body, first, second):
    while (body.find(first) > 0 and body.find(second, body.find(first) + 1) > 0):
        body1 = body[0: body.find(first)]   # first part
        if body.find(second, body.find(first)) > 0:
            body2 = body[body.find(second, body.find(first) + 1) + len(second):-1]  #second part
            body = body1 + body2
    return body

def removeitems(body):
    removetheseitems = ('<p>',"</p>","<br/>","<li>","</li>", "</div>","<div","<h2>","</h2>","<h3>","</h3>","<!DOCTYPE html>","<span>","</span>")
    newbody = []
    for line in body:
        for x in removetheseitems:
            line = line.replace(x,"")
        newbody.append(line)
    return newbody

def getwebsitecopy(webpagelink, ordernumber):   #ordernumber in reverse 
    web, date = [],[] #resets
    if isinstance(ordernumber,(str)):   # find all pages saved in days before
        if ordernumber[-1] == "d" or ordernumber[-1] == "D":
            try:
                daystoget = int(ordernumber[:-1])
            except:
                print("don't understand input:", ordernumber)
                return False, False
        todaysdate = datetime.datetime.utcnow()  
        newdatetime = todaysdate.replace(hour=0, minute=0, second=0)  #reset date to the previous midnight to get a full day
        delta = datetime.timedelta(daystoget)
        newdatetime = newdatetime - delta

        aggregationpipeline = [{ '$match': { 'webpagelink': webpagelink }}, {'$unwind': {  'path': '$copy'  }
        }, {'$match': { 'copy.date': { '$gte': newdatetime }}}]#, {  '$unset': 'copy.content'  } ]  for testing - not fetching we site contents

    if isinstance(ordernumber,(int,float)):   # if number of pages before ignoring days
        aggregationpipeline = [ { '$match': {'webpagelink': webpagelink }}, {
        '$project': { 'copy': { '$slice': [ '$copy', -ordernumber ]}}}, {'$unwind': { 'path': '$copy' }}]

    loadeddata = dbupdate[collectionnameinmongodb].aggregate(aggregationpipeline) 

    for onepage in loadeddata:
        web.append(bz2.decompress(onepage["copy"]["content"]))
        date.append(onepage["copy"]["date"])
    return web, date   # return list of webpages and dates

def getlistofwebsites():  # gets a list of websites for the initial menu
    loadeddata = dbupdate[collectionnameinmongodb].find({} ,{'copy.content':0}) # read all data exept for saved webpages
    websitenamearray = []
    websitesizearray = []
    websitedatearray = []
    websitecopies = []
    for post in loadeddata:
        try:
            if post['webpagelink'] not in websitenamearray:
                websitenamearray.append(post['webpagelink'])
                if post["copy"] != []:
                    newestentry = max(post["copy"], key = lambda x: x["date"])
                else: 
                    print("some error at", post['webpagelink'])
                    newestentry = {'size':"","date":"","copy":""}
                websitesizearray.append(newestentry['size'])
                websitedatearray.append(newestentry["date"])
                websitecopies.append(len(post["copy"]))
        except: exit("some database error or data mismatch")
    return websitenamearray, websitesizearray,websitedatearray,websitecopies

def cleanhtmlpage(body):
    body = gettitle(body,"<body>","</body>")  # work only with code enclosed by body tag
    removeelements = (("<script","</script>"),("<div class=\"","\">"),("<div class=\"","\">"),("<div class=\'","\">"),
    ("<input","/>"),("<!-- END","-->"),("<!-- BEGIN","-->"),("<button>","</button>"),("<span",">"))#,("<path",">"))  
    for x in removeelements:
        body = removecodes(body, *x)   #  body = removecodes(body1,"<first tag>","</second tag>")
    lines = body.split("\n")   # split html into lines 
    lines = [x for x in lines if x.strip()]  # remove empty spaces
    return lines

def main():
    global dbupdate, collectionnameinmongodb   
    datebasenameinmongodb = settings.DATABASE  # datebase name here 
    collectionnameinmongodb = settings.COLLECTION  # collection name 
    try:
#  MongoDb connection string, get by creating seperate use access login in MongoDband white listing ip address where script is run
        client = MongoClient(settings.URI) # saved in settings.py file      
        dbupdate = client[datebasenameinmongodb]
        listofwebsites, listofwebsitesizes, listofwebsitedates,listofwebsitecopies = getlistofwebsites()
    except:
        print('error accessing the databse...')
        return

    numberofwebsites = len(listofwebsites)
    print("currently in the \"", collectionnameinmongodb, "\" collection are " , str(numberofwebsites)," websites ", "\x1b[92m","(green ones are updated today UTC)","\x1b[39m", ":", sep ="")
    datenow = datetime.datetime.utcnow()
    for count, webl in enumerate(listofwebsites):
        print('\033[1;33m', count + 1, '\033[0;0m',". " ,("\x1b[92m" if datenow.day == listofwebsitedates[count].day else "\x1b[39m" ), webl, "\x1b[39m"," (" ,listofwebsitecopies[count],")", end = " ",sep = "")
    userinput = input(f"\nNumber for website to analyze (or # before number to remove the last entry): ") 
    if (str(userinput).isnumeric() == True):
        k = int(userinput)
        try:
            print("going to read saved website: ", listofwebsites[k-1])
        except:
            print("number out of range. exiting")
            return
        versions = input("Number of \x1b[4mprevious versions\x1b[24m to compare (hit Enter for default value of 2) or Key number and d for \x1b[4mnumber of days\x1b[24m, for example 2d :") or 2
        if (str(versions).isnumeric() == True):
            versions = int(versions) 
        lines1, lines2 = [],[]
        output1, date1 = getwebsitecopy(listofwebsites[k-1],versions)  
        if output1 == False:
            print("last array empty. exiting...")
            return
        for i in range(len(date1)):
            output = str(output1[i]).encode().decode('unicode_escape').encode('latin1').decode()  # utf-8
            lines1 = cleanhtmlpage(output)
            print("Title is:",'\033[1;33m', gettitle(output,"<title","</title>"), '\033[0;0m')
            print("line count now:", len(lines1), " date: ", date1[i].strftime("%Y-%m-%d %H:%M"))
            if lines2 == []:
                lines2 = lines1
                continue
            print("-"*27," ADDED ","-"*27)
            added = list(set(lines1) - set(lines2))
            added = removeitems(added)
            for linebyline in added:
                print(linebyline.strip())
            print("-"*26," REMOVED ","-"*26)
            removed = list(set(lines2) - set(lines1))
            removed = removeitems(removed)
            for linebyline in removed:
                print(linebyline.strip()) 
        print("-"*29," END ","-"*29)
    else: 
        if userinput.startswith("#"):  # this part just removes last entry in the database
            if (str(userinput[1:]).isnumeric() == True):
                k = int(userinput[1:])
                if k <= len(listofwebsites):
                    print("going to delete: ", listofwebsites[k-1])
                    webpagelink = listofwebsites[k-1]
                    deleteresult = dbupdate[collectionnameinmongodb].update_one({"webpagelink":webpagelink},{"$pop": {"copy":1} }) 
                    print("results of deletion: ",deleteresult)

if __name__ == "__main__":
    main()
