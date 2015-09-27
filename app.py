import scraper
import re
from flask import Flask, render_template, request
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
        # check whether the user provided a valid day, otherwise use today
        day_param = request.args.get('day')
        if day_param is not None and verify_date_param(day_param):
            coursedata = scraper.scrape(course, day_param)
        else:
            coursedata = scraper.scrape(course)
        # this data is from one particular course
        # we take the individual moments and put them in the dict, separated by day
        bucketadd(entries_by_day, "day", coursedata)

    # this will end up containing Weekday objects, which also contain the courses for that day
    weekdays_with_courses = [] 
    for date, entries in entries_by_day.items():
        weekdays_with_courses.append(Weekday(date, entries))

    # sort the Weekdays based on their weekindex, so monday comes first and sunday last
    sorted_data = sorted(weekdays_with_courses, key=lambda x: x.weekindex)
    print(sorted_data)
    return render_template("lookup.html", days=sorted_data)

# Used to reformat the datastructures from a per-course basis to a per-day basis
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

# turn something like "Wednesday 30 September 2015" into 2 (the index of wednesday in a week)
def getWeekIndex(name):
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for i, day in enumerate(weekdays):
        if day in name.lower():
            return i
    # if we can't find where it belongs, just put it at the end I guess?
    return 7

# verify that the url argument is a date in the format that SAP expects, e.g. 27.09.2015
def verify_date_param(datestring):
    date_re = re.compile("\d\d\.\d\d\.\d\d\d\d")
    return date_re.match(datestring) is not None

if __name__ == '__main__':
    app.run(debug=True)
