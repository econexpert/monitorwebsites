from async_timeout import timeout
from pymongo import MongoClient
import datetime
import urllib3
from sys import exit
import bz2

class getwebsite:
    def __init__(self,websitename):
        self.websitename = websitename

    def getwebsitesize(self,websitename):
        http = urllib3.PoolManager()
        headers = {'user-agent':"Mozilla/5.0 (Windows NT 6.3; rv:36.0) .."}
        print('now getting: ' + websitename)
        try:
            response = http.request('GET', websitename, timeout = 1.5, headers = headers) 
        except urllib3.exceptions.MaxRetryError as e:
            print("error getting this website: ", '\033[1;31m', websitename, '\033[0;0m')
            return 0
        except urllib3.exceptions.ReadTimeoutError as e:
            print("error getting this website: ", '\033[1;31m', websitename, '\033[0;0m')
            return 0
        self.webpagehtml = response.data
        return len(response.data)

    def getcompressedweb(self):
        self.compressedhtml = bz2.compress(self.webpagehtml)   # compress to binary
        print("size of compressed data: ", len(self.compressedhtml), round(len(self.compressedhtml)/len(self.webpagehtml),4)*100 ,"%")
        return self.compressedhtml
    def getwebtitle(self):
        pagehtml = str(self.webpagehtml)
        title = pagehtml[pagehtml.find("<title>") + 7: pagehtml.find("</title>")]
        return title

def updatenewdata(webpagelink,size, compressed, maxcopiestokeep = 20):
    first = {'webpagelink': webpagelink}
    second = {'$push':{'copy': {'$each': [{"remarks":"none", "size": size, "date": datenow, "content": compressed}], '$slice': -maxcopiestokeep}}}
    updateresult = dbupdate[collectionnameinmongodb].update_one(first, second)
    print("updates made: " + str(updateresult.modified_count))

def deleteolddata(webpagelink,maxcopiestokeep = 20):
    first = {'webpagelink': webpagelink}
    second = {'$push':{'copy': {'$each':[],'$slice': -maxcopiestokeep }}}

    updateresult = dbupdate[collectionnameinmongodb].update_one(first, second)
    print("deletions made: " + str(updateresult.modified_count))

def adddatabase(websitename):
    nevv = getwebsite(websitename)
    size = int(nevv.getwebsitesize(websitename))
    if size > 0:
        print("website to be updated: " + nevv.getwebtitle() + " and size: " + str(size))
        first = {"webpagelink": websitename, "copy": [{"remarks": "none", "size": size,"date": datenow,"content": nevv.getcompressedweb() }] }
        x = dbupdate[collectionnameinmongodb].insert_one(first)
        print("insertion made with id: " + str(x.inserted_id))

def deletewebsitefromdatabase(websitelink):
    print("website link to be deleted: " + websitelink)
    first = {"webpagelink": websitelink}
    x = dbupdate[collectionnameinmongodb].delete_many(first)
    print("deletions made: " + str(x.deleted_count))

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
                    newestentry['size'] = ""
                    newestentry['date'] = ""
                    newestentry['copy'] = ""

                websitesizearray.append(newestentry['size'])
                websitedatearray.append(newestentry["date"])
                websitecopies.append(len(post["copy"]))
        except: exit("some database error or data mismatch")
    return websitenamearray, websitesizearray,websitedatearray,websitecopies

def main(updateallandquit = False):
    global datenow, dbupdate, collectionnameinmongodb   
    tolerance = 48  # tolerance in Kb
    copiestokeep = 30   # number of copies to keep of websites, oldest are deleted
    datebasenameinmongodb = "testme-database"  # change datebase name here if needed   
    collectionnameinmongodb = "testme-collection"  # change collection name here if needed 
    navv = getwebsite("")
    datenow = datetime.datetime.utcnow()

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
    print("currently in the \"", collectionnameinmongodb, "\" collection are " , str(numberofwebsites)," websites ", "\x1b[92m","(green ones were updated today UTC)","\x1b[39m", ":", sep ="")
    datenow = datetime.datetime.utcnow()
    for count, webl in enumerate(listofwebsites):
        print('\033[1;33m', count + 1, '\033[0;0m',". " ,("\x1b[92m" if datenow.day == listofwebsitedates[count].day else "\x1b[39m" ), webl, "\x1b[39m"," (" ,listofwebsitecopies[count],")", end = " ",sep = "")
    print(f"\ntolerance level at Kb: " + str(tolerance) + " copies to keep: " + str(copiestokeep))
    if updateallandquit:
        userinput = ""
        print("updating all and quiting")
    else:
        userinput = input("website link for addition, number for deletion, blank for update of database: ") 
    if (str(userinput).isnumeric() == True):
            try: 
                deletewebsitefromdatabase(listofwebsites[int(userinput)-1])
                print("delete finished")
            except: 
                print("couldn't delete website")
            return
    else:
        if (str(userinput) != ""):
            if str(userinput) not in listofwebsites:
                adddatabase(userinput)
            else:
                print("trying to add duplicate...")
            return
    print("going to update whole datebase...")
    for k in range(numberofwebsites):
        print(k+1,". ", "-"*55, sep = "")
        size = navv.getwebsitesize(listofwebsites[k])   #this gets new size of website
        if listofwebsitesizes[k] == "":   # checks if database array data is not empty
            listofwebsitesizes[k] = 0
            listofwebsitedates[k] = datetime.datetime.utcnow() 
        if (size > 0 and (abs(listofwebsitesizes[k] - size) > tolerance)):   
            print("Updating now:",'\033[1;33m', navv.getwebtitle(), '\033[0;0m')
            print('\033[1;32m' + listofwebsites[k] +'\033[0;0m' + " updated from " + listofwebsitedates[k].strftime("%Y-%m-%d %H:%M") + " with current date: " + datenow.strftime("%Y-%m-%d %H:%M") + " current size " + str(size) + " from old size " + str(listofwebsitesizes[k]))
            updatenewdata(listofwebsites[k],size, navv.getcompressedweb(), copiestokeep)
        else:
            print('website not updated. Current size: ' + str(size) + ' old size: ' + str(listofwebsitesizes[k]))
if __name__ == "__main__":
    main(updateallandquit = True)  # this one to true if running as scheduled job in cloud, false to desplay menu: to add new urls or delete
