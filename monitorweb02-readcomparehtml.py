from async_timeout import timeout
from pymongo import MongoClient
from sys import exit
import bz2
import datetime

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
    loadeddata = dbupdate[collectionnameinmongodb].find({"webpagelink":webpagelink}, { "copy": { "$slice": [-ordernumber,1] } }) 
    if loadeddata[0]["copy"] == []: #return if no data
        return False,False
    web = bz2.decompress(loadeddata[0]["copy"][0]["content"])
    date = loadeddata[0]["copy"][0]["date"]
    return web, date

def getlistofwebsites():
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
    datebasenameinmongodb = "webpages01"  # change datebase name here if needed   
    collectionnameinmongodb = "webpages01"  # change collection name here if needed 
    try:
#  mongoDb connection string, to be kept secret, replace new_user_name_for_python and new_user_password_for_python with database user login and password, white list your IP address to MongoDb
#  more on https://www.mongodb.com/docs/atlas/tutorial/connect-to-your-cluster/
        client = MongoClient("mongodb+srv://new_user_name_for_python:new_user_password_for_python@better_copy_string_from_atlas.mongodb.net/")       
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
    userinput = input(f"\nNumber for website to analyze (or # before number to remove last entry): ") 
    if (str(userinput).isnumeric() == True):
        k = int(userinput)
        print("going to read saved website...", listofwebsites[k-1])
        output1, date1 = getwebsitecopy(listofwebsites[k-1],1)
        if output1 == False:
            print("last array empty. exiting...")
            return
        output2, date2 = getwebsitecopy(listofwebsites[k-1],2)

        output1 = str(output1).encode().decode('unicode_escape').encode('latin1').decode() 
        output2 = str(output2).encode().decode('unicode_escape').encode('latin1').decode() 

        lines1 = cleanhtmlpage(output1)
        print("Title is:",'\033[1;33m', gettitle(output1,"<title","</title>"), '\033[0;0m')
        lines2 = cleanhtmlpage(output2)  
        print("line count before:",len(lines2), " date: ", date2.strftime("%Y-%m-%d %H:%M"))
        print("line count now:", len(lines1), " date: ", date1.strftime("%Y-%m-%d %H:%M"))
        print("-"*25," ADDED ","-"*25)
        added = list(set(lines1) - set(lines2))
        added = removeitems(added)
        for linebyline in added:
            print(linebyline.strip())
        print("-"*24," REMOVED ","-"*24)
        removed = list(set(lines2) - set(lines1))
        removed = removeitems(removed)
        for linebyline in removed:
            print(linebyline.strip()) 
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
