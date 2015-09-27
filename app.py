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
    data = scrape.scrape(courses[0])
    return render_template("lookup.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)
