from pymongo import MongoClient
import datetime
import pandas as pd
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def preparehtml(content, days, timenow, startdate):
    html = """<html> <head> <style>
    table {
      font-family: arial, sans-serif;
     border-collapse: collapse;
        width: 98%;
    }
    th, td {
        border: 1px solid black;
    }
    th, td {
        padding: 5px;
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 90%;
    }
    thead { background-color: #cccccc; }
     </style> </head> 
     <body> <p>Hi!<br><p> Webmontor summary for the last <b>"""  
    html += str(days) + "</b> days from " + str(startdate) + "</p>" + content.to_html(header = False, render_links=True, bold_rows = False) 
    html +=  " <br>  Prepared on " + str(timenow) + " (UTC time) </body></html>"
    replace = [ ("name", "Monitored Links"), ("day_of_week", "Weekday"),("<th></th>","<th>Updates</th>")] # final formating before returning html
    for old, new in replace: 
        html = html.replace(old, new, 1) # first row finishings 
    return html

def sendhtmlmail(toaddrs,content, days, timenow, startdate):
    print("trying to send e-mail...")
    fromaddr = "user@server.com"  # from addresss
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Webmonitor summary of the last " + str(days) + " days" 
    msg['From'] = fromaddr
    msg['To'] = toaddrs

    text = content.to_string()  # for text only e-mail, this part sourced from stackoverflow 
    html = preparehtml(content, days, timenow, startdate)
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # source  https://stackoverflow.com/questions/882712/send-html-emails-with-python 
    msg.attach(part1)
    msg.attach(part2)
    try:
        server = SMTP('SMTPserver',587)   # SMTP server address and port number, usually 587, 465 etc.
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login('login@server.com', 'SMTPpassword')   # SMTP login name and password
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.quit()
        print("done sending e-mails")
    except:
        print("some issues with e-mail!")

def getlistofwebsites():
    loadeddata = dbupdate[collectionnameinmongodb].find({},{'copy.content':0}) # read all data exept for saved webpages
    websitenamearray = []
    websitesizearray = []
    websitedatearray = []
    websitecopies = []
    secondnamearray = []
    for post in loadeddata:
        try:
                if post["copy"] != []:
                    websitenamearray.append(post['webpagelink'])
                    websitecopies.append(len(post["copy"]))

                    for dudu in post["copy"]:
                        websitesizearray.append(dudu['size'])
                        websitedatearray.append(dudu["date"])
                        secondnamearray.append(post["webpagelink"])
                else: 
                    print("some error at", post['webpagelink'])
                    newestentry = {'size':"","date":"","copy":""}
        except: exit("some database error or data mismatch")
    return websitenamearray, websitesizearray,websitedatearray,websitecopies, secondnamearray

def main(howmanydays):
    global dbupdate, collectionnameinmongodb   
    datebasenameinmongodb = "webpages01"  # change datebase name here if needed   
    collectionnameinmongodb = "webpages01"  # change collection name here if needed 
    toaddrs  = "user@server.com"   # to address where to send summary
    try:
#  mongoDb connection string, to be kept secret, replace new_user_name_for_python and new_user_password_for_python with database user login and password, white list your IP address to MongoDb
#  more on https://www.mongodb.com/docs/atlas/tutorial/connect-to-your-cluster/
        client = MongoClient("mongodb+srv://long_as_cluster_user:password_as_cluster_user@server.mongodb.net")  # MongoDb connection string     
        dbupdate = client[datebasenameinmongodb]
        listofwebsites, listofwebsitesizes, listofwebsitedates,listofwebsitecopies, secondnamearray = getlistofwebsites()
    except:
        print('error accessing the databse...')
        return

    numberofwebsites = len(listofwebsites)
    print("currently in the \"", collectionnameinmongodb, "\" collection are " , str(numberofwebsites)," websites ", "\x1b[92m","(green ones are updated today UTC)","\x1b[39m", ":", sep ="")
    datenow = datetime.datetime.utcnow()
    for count, webl in enumerate(listofwebsites):
        print('\033[1;33m', count + 1, '\033[0;0m',". " ,("\x1b[92m" if datenow.day == listofwebsitedates[count].day else "\x1b[39m" ), webl, "\x1b[39m"," (" ,listofwebsitecopies[count],")", end = " ",sep = "")
    if howmanydays == 0:   
        userinput = input(f"\nNumber of days to summarize: ") 
        if (str(userinput).isnumeric() == True):
            howmanydays = int(userinput)
        else:
            print("input not understood")
            return

    startdate = datenow - datetime.timedelta(days=howmanydays)
    table = pd.DataFrame({"dates": listofwebsitedates, "name": secondnamearray, "size": listofwebsitesizes})
    table = table.loc[table['dates'] > startdate]
    table['day_of_week'] = pd.DatetimeIndex(table['dates']).day_name()
    table['dates'] = pd.to_datetime(table['dates']).dt.date
    finaltable = table.groupby(['name','dates','day_of_week'], as_index = True).size().to_frame('updates') # pandas data summmary 
    
    print("-"*27," SUMMARY ","-"*27)  # summary for monitoring
    print(finaltable) 
    print("-"*29," END ","-"*29)
    print("prepared on:", datenow.strftime('%y-%m-%d %A %H:%M:%S'))

    text_file = open("summary.html", "w")
    text_file.write(preparehtml(finaltable,howmanydays, datenow.strftime('%y-%m-%d %A %H:%M:%S'), startdate.strftime('%y-%m-%d %A %H:%M:%S'))) # comment out if not saving html file
    text_file.close()
    sendhtmlmail(toaddrs, finaltable, howmanydays, datenow.strftime('%y-%m-%d %A %H:%M:%S'), startdate.strftime('%y-%m-%d %A %H:%M:%S')) # comment out if not sending e-mail

if __name__ == "__main__":
    main(howmanydays = 0)  # how many days to sumarize and quit. If 0 value, then menu is offered 
