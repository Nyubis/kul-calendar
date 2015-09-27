import re
import requests
from datetime import datetime, timedelta

course_url_template = "http://www.kuleuven.be/sapredir/uurrooster/pre_laden.htm?OBJID={}&OTYPE=SM&TAAL=E&SEL_JAAR=2015"

hidden_re = re.compile('<input type="hidden" name="([^"]+)" value="([^"]+)">')
font_re   = re.compile("<font[^>]+>([^<]+)</font>", re.IGNORECASE)
space_re  = re.compile("\r\n +(&nbsp;)?")
txt_re    = re.compile('<td.+?class="txt".+?>(.+?)</td>', re.DOTALL) # the dotall is there so that it can capture \r\n

def scrape(coursecode, date=datetime.now()):
    # start the request chain for the timetable of the given course
    first = requests.get(course_url_template.format(coursecode))
    # we get redirected to a page where js is used to submit a form full of hidden fields.
    # we extract the fields with a regex, change the date to the provided one, and submit the form manually
    fparams = dict(hidden_re.findall(first.text))
    fparams['nieuwedatum'] = date.strftime("%d.%m.%Y")
    second = requests.post(first.url, params=fparams, cookies=first.cookies)
    # we're on the standard timetable page now, but the data is displayed in a table that's a nightmare to scrape
    # so we post another form that will redirect us and give us the same data in a slightly saner format
    third = requests.post(second.url, params={"onInputProcessing(printversie)": ""}, cookies=second.cookies)
    # this is some dumb loader page that uses javascript to get our user agent and more stuff
    # it doesn't really matter, submit the form with most data empty and get redirected again
    uaparams={"browser": "", "version": "", "platform": "", "objid": "00000000", "otype": "", "OnInputProcessing(verder)": ""}
    fourth = requests.post(third.url, params=uaparams, cookies=third.cookies)
    # this one contains the actual data in a somewhat legible format, so we extract it with even more regexes
    extract_data(fourth.text)

def extract_data(html):
    # the date is in between font tags with a whole lot of whitespace crap around it
    raw_days = font_re.findall(html)
    clean_days = list(map(lambda x: space_re.sub(" ", x.strip()), raw_days))
    print(clean_days)
    # the other data is in td tags with class="txt"
    raw_data = txt_re.findall(html)
    clean_data = list(map(lambda x: x.replace("<!--          </FONT> -->", "").replace("&nbsp;", "").strip(), raw_data))
    print(clean_data)
    

