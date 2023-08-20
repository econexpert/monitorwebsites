from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import monitorweb02
import settings
import datetime

app = Flask(__name__)
  
# Create a MongoDB client
client = MongoClient(settings.URI)
db = client[settings.DATABASE]
collection = db[settings.COLLECTION]

navv = monitorweb02.getwebsite("")
datenow = datetime.datetime.utcnow()

@app.route('/')
def index():
    # Retrieve data from the collection
    listofwebsites, listofwebsitesizes, listofwebsitedates,listofwebsitecopies = monitorweb02.getlistofwebsites(collection)
    kopa = [{'webpagelink':site, 'webpagesize': f"{size:,}", 'webpagedate': str(date).split('.')[0], 'webpagecopies': copies, "today":date.day == datenow.day} for site, size, date, copies in zip(listofwebsites, listofwebsitesizes, listofwebsitedates, listofwebsitecopies)]
    totalpages = str(len(listofwebsites))
    return render_template('index.html', data=kopa, totalpages = totalpages)

@app.route('/update', methods=['POST'])
def update_data():
    field1_value = request.form.get('field1')
    monitorweb02.adddatabase(field1_value, collection, datenow)
    return redirect(url_for('index'))

@app.route('/delete_last', methods=['POST'])
def delete_last_record():
    # Delete the last record in the collection
    listofwebsites, listofwebsitesizes, listofwebsitedates,listofwebsitecopies = monitorweb02.getlistofwebsites(collection)
    deleteentry = int(request.form.get('number'))
    try:
        monitorweb02.deletewebsitefromdatabase(listofwebsites[deleteentry-1], collection)
    except:
        print("no etries deleted")
    return redirect(url_for('index'))

@app.route('/check', methods=['POST'])
def check_all():
    # Delete the last record in the collection
    print("checking all websites for updates")
    monitorweb02.updateall(40,500,navv, collection)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
