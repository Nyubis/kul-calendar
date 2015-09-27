import scrape
from flask import Flask, render_template
from datetime import datetime, timedelta
app = Flask(__name__)

@app.route("/")
def home():
    return "Add your course numbers to the url, separated with +"

@app.route("/<coursestring>")
def lookup(coursestring):
    courses = coursestring.split("+")
    entries_by_day = {}
    for course in courses:
        coursedata = scrape.scrape(course)
        bucketadd(entries_by_day, "day", coursedata)
    
    weekdays_with_courses = []
    for date, entries in entries_by_day.items():
        weekdays_with_courses.append(Weekday(date, entries))
    
    sorted_data = sorted(weekdays_with_courses, key=lambda x: x.weekindex)
    print(sorted_data)
    return render_template("lookup.html", days=sorted_data)

# Used to reformat the datastructures on a per-course basis to a per-day basis
def bucketadd(dictionary, key, entries):
    for entry in entries:
        if entry[key] in dictionary:
            dictionary[entry[key]].append(entry)
        else:
            dictionary[entry[key]] = [entry]
    # no need to return anything, we have a reference to dictionary so the original one has changed too

# used to store all the courses info of a particular day
class Weekday:
    def __init__(self, name, entries):
        self.name = name
        self.entries = entries
        self.weekindex = getWeekIndex(name)
    def addentry(self, entry):
        self.entries.append(entry)

def getWeekIndex(name):
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for i, day in enumerate(weekdays):
        if day in name.lower():
            return i
    # if we can't find where it belongs, just put it at the end I guess?
    return 7

if __name__ == '__main__':
    app.run(debug=False)
