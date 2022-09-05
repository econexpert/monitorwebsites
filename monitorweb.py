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
        print('now getting website: ' + websitename)
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
        self.compressedhtml = bz2.compress(self.webpagehtml)   # compress to binary, save for later use
        print("size of compressed data: ", len(self.compressedhtml))
        return self.compressedhtml
    def getwebtitle(self):
        pagehtml = str(self.webpagehtml)
        title = pagehtml[pagehtml.find("<title>") + 7: pagehtml.find("</title>")]
        return title

def updatenewdata(webpagelink,size, compressed):
    first = {"webpagelink": webpagelink}
    second = {"$set": {"remarks": "none", "size": size, "date": datenow, "content": compressed}}
    updateresult = dbupdate[collectionnameinmongodb].update_many(first, second)
    print("updates made: " + str(updateresult.modified_count))
    return

def adddatabase(websitename):
    nevv = getwebsite(websitename)
    size = int(nevv.getwebsitesize(websitename))
    if size > 0:
        print("website to be updated: " + nevv.getwebtitle() + " and size: " + str(size))
        first = {"webpagelink": websitename, "remarks": "none", "size": size,"date": datenow,"content": nevv.getcompressedweb()  }
        x = dbupdate[collectionnameinmongodb].insert_one(first)
        print("insertion made with id: " + str(x.inserted_id))

def deletewebsitefromdatabase(websitelink):
    print("website link to be deleted: " + websitelink)
    first = {"webpagelink": websitelink}
    x = dbupdate[collectionnameinmongodb].delete_many(first)
    print("deletions made: " + str(x.deleted_count))
    return

def getlistofwebsites():
    loadeddata = dbupdate[collectionnameinmongodb].find({},{'content':0}) # read all data exept for saved webpages
    websitenamearray = []
    websitesizearray = []
    websitedatearray = []
    for post in loadeddata:
        try:
            if post['webpagelink'] not in websitenamearray:
                websitenamearray.append(post['webpagelink'])
                websitesizearray.append(post['size'])
                websitedatearray.append(post['date'])
        except: exit("some database error or data mismatch")
    return websitenamearray, websitesizearray,websitedatearray

def main():
#  mongoDb connection string, to be kept secret, replace new_user_name_for_python and new_user_password_for_python
    client = MongoClient("mongodb+srv://new_user_name_for_python:new_user_password_for_python@copy_string_from_atlas.mongodb.net/")       
    global datenow, dbupdate, collectionnameinmongodb   
    tolerance = 40  # tolerance in Kb
    datebasenameinmongodb = "testme-database"  # change datebase name here if needed 
    collectionnameinmongodb = "testme-collection"  # change collection name here if needed
    navv = getwebsite("")
    datenow = datetime.datetime.utcnow()

    try:
        dbupdate = client[datebasenameinmongodb]
        listofwebsites, listofwebsitesizes, listofwebsitedates = getlistofwebsites()
    except:
        print('error accessing the databse...')
        return

    numberofwebsites = len(listofwebsites)
    print("currently in the database" , str(numberofwebsites)," websites: ")
    for count, webl in enumerate(listofwebsites):
        print('\033[1;33m', count + 1, '\033[0;0m' , webl, end = " ")
    print(f"\ntolerance level at Kb: " + str(tolerance))
    userinput = input("website link for addition, number for deletion, blank for update of database: ") 
    if (str(userinput).isnumeric() == True):
            try: 
                deletewebsitefromdatabase(listofwebsites[int(userinput)-1])
                print("delete finished")
            except: 
                print("couldn't delete website")
            exit()
    else:
        if (str(userinput) != ""):
            if str(userinput) not in listofwebsites:
                adddatabase(userinput)
            else:
                print("trying to add duplicate...")
            exit()
    print("going to update whole datebase...")
    for k in range(numberofwebsites):
        print(" ---------------------------------------------------------------- ")
        size = navv.getwebsitesize(listofwebsites[k]) 
        if (size > 0 and (abs(listofwebsitesizes[k] - size) > tolerance)):   
            print("Updating now:",'\033[1;33m', navv.getwebtitle(), '\033[0;0m')
            print('\033[1;32m' + listofwebsites[k] +'\033[0;0m' + " was updated from " + listofwebsitedates[k].strftime("%Y-%m-%d %H:%M") + " with current date: " + datenow.strftime("%Y-%m-%d %H:%M") + " from old size " + str(listofwebsitesizes[k]))
            updatenewdata(listofwebsites[k],size, navv.getcompressedweb())
        else:
            print('website not updated. Current size is: ' + str(size) + ' old size: ' + str(listofwebsitesizes[k]))

if __name__ == "__main__":
    main()
