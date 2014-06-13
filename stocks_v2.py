#/usr/bin/python

# Written by @senilio

import os
import urllib
import json
from time import sleep,time

stocks = {}

####### Start user config
stocks["EKTA"] = ["YAHOO", "EKTA-B.ST", "SEK"]
stocks["WFM"] = ["YAHOO", "WFM", "USD"]
stocks["SWMA"] = ["GOOGLE", "STO:SWMA", "SEK"]
stocks["FING"] = ["GOOGLE", "STO:FING-B", "SEK"]
stocks["BOL"] = ["GOOGLE", "STO:BOL", "SEK"]
stocks["MTG"] = ["GOOGLE", "STO:MTG-B", "SEK"]
stocks["OMX30"] = ["YAHOO", "^OMX", "PKT"]
stocks["TELE2"] = ["GOOGLE", "STO:TEL2-B", "SEK"]
stocks["VOLVO"] = ["GOOGLE", "STO:VOLV-B", "SEK"]
stocks["DAX30"] = ["YAHOO", "^GDAXI", "EUR"]
stocks["ETX"] = ["GOOGLE", "STO:ETX", "SEK"]
stocks["GOLD"] = ["YAHOO", "GCQ14.CMX", "USD"]
stocks["COPPER"] = ["YAHOO", "HGM14.CMX", "USD"]
stocks["NEXAM"] = ["YAHOO", "NEXAM.ST", "SEK"]
stocks["AMAYA"] = ["YAHOO", "AYA.TO", "CAD"]

# Time to sleep between polls
sleeptime = 30

# Use colors or no?
colors = True

# Debug mode
debug = False

# Google Finance URL
google_base_url = 'http://finance.google.com/finance/info?client=ig&q='

# Yahoo Finance URL
yahoo_base_url = 'http://finance.yahoo.com/d/quotes.csv?s='
yahoo_url_suffix = '&f=l1cs'

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = "\033[1m"

# END OF CONFIG, START OF SCRIPT

def green(msg):
    return GREEN + msg + ENDC

def yellow(msg):
    return YELLOW + msg + ENDC

def red(msg):
    return RED + msg + ENDC

def GoogleQuote(data):
    for x in stocks:
        if stocks[x][1] == data['t'] or stocks[x][1] == data['e']+':'+data['t']:
            try:
                tempval = stocks[x][3][0]
            except IndexError:
                tempval = stocks[x][4]
            stocks[x][3] = []

            if debug: print "Creating stock data for " + x
            value = data['l_fix'][:7]
            if value == stocks[x][4] or stocks[x][4] == 9999:
                stocks[x][4] = value
                stocks[x][3].append(str(value))
            elif value < stocks[x][4]:
                stocks[x][4] = value
                stocks[x][3].append(str(value))
            elif value > stocks[x][4]:
                oldrate = value
                stocks[x][3].append(str(value))
            stocks[x][4] = tempval

            if debug: print "Creating stock percent for " + x
            value = data['cp_fix'][:5]
            if float(value) < 0:
                stocks[x][3].append(str(value))
            elif float(value) > 0:
                stocks[x][3].append(str('+'+value))
            else:
                stocks[x][3].append(str(" "+value))

            if debug: print "Creating stock change for " + x
            value = data['c_fix'][:5]
            currency = stocks[x][2]
            if float(value) < 0:
                stocks[x][3].append(str(value))
            elif float(value) > 0:
                stocks[x][3].append(str('+'+value))
            else:
                stocks[x][3].append(str(" "+value))

    if debug: print "Finished " + x

def YahooQuote(string):
    data = string.split(",")
    ticker = data[2][1:-1]
    for x in stocks:
        if stocks[x][1] == ticker:
            try:
                tempval = stocks[x][3][0]
            except IndexError:
                tempval = stocks[x][4]
            stocks[x][3] = []
            if debug: print "Creating stock quote for " + x
            value = data[0][:7]
            if value == stocks[x][4] or stocks[x][4] == "9999":
                stocks[x][4] = value
                stocks[x][3].append(str(value))
            elif value < stocks[x][4]:
                stocks[x][4] = value
                stocks[x][3].append(str(value))
            elif value > stocks[x][4]:
                stocks[x][4] = value
                stocks[x][3].append(str(value))
            stocks[x][4] = tempval

            value = data[1].split(" - ")[1][:-2]
            value = value[:5]
            if float(value) < 0:
                stocks[x][3].append(str(value[:5]))
            elif float(value) > 0:
                stocks[x][3].append(str(value[:5]))
            else:
                stocks[x][3].append(" "+str(value))

            if debug: print "Creating stock change for " + x
            value = data[1].split(" - ")[0][1:6]
            currency = stocks[x][2]
            if float(value) < 0:
                stocks[x][3].append(str(value))
            elif float(value) > 0:
                stocks[x][3].append(str(value))
            else:
                if value[0] == '-' or value[0] == '+':
                    value = value[1:]
                stocks[x][3].append(" "+str(value))

            if debug: print "Finished " + x


def color1(val,oldval):
    # color1 function compares first and second value,
    # and print first value in red, green or no color accordingly.
    if not colors:
        return val
    if val == oldval or oldval == "9999":
        return val
    if val < oldval:
        return red(val)
    elif val > oldval:
        return green(val)

def color2(pre, val, post):
    # color2 function colors pre+val+post depending on
    # if val is <0 >0 or 0
    if not colors:
        return str(pre+val+post)
    if float(val) < 0:
        return red(pre+val+post)
    elif float(val) > 0:
        return str(green(pre+val+post))
    else:
        return str(pre+val+post)

### START

# COLLECT YAHOO STOCKS
yahoo_stocks = ""
for i in stocks:
    if stocks[i][0] == "YAHOO":
        if not yahoo_stocks:
            yahoo_stocks = stocks[i][1]
        else:
            yahoo_stocks = yahoo_stocks + "+" + stocks[i][1]

# COLLECT GOOGLE STOCKS
google_stocks = ""
for i in stocks:
    if stocks[i][0] == "GOOGLE":
        if not google_stocks:
            google_stocks = stocks[i][1]
        else:
            google_stocks = google_stocks + "," + stocks[i][1]

# CREATE LAST PRICE ENTRY AND DATA LIST
for i in stocks:
    stocks[i].append([])
    stocks[i].append("9999")

while True:
    start_time = time()
    datum =  os.popen("date").read().rstrip()

    # GET YAHOO STOCK DATA
    yahoo_data=urllib.urlopen(yahoo_base_url+yahoo_stocks+yahoo_url_suffix).read().rstrip().split('\n')
    for i in yahoo_data:
        YahooQuote(i.rstrip())

    # GET GOOGLE STOCK DATA
    google_data=urllib.urlopen(google_base_url+google_stocks).read()
    obj = json.loads(google_data[3:])
    for i in obj:
        GoogleQuote(i)

    # OUTPUT DATA
    print datum
#    for key in sorted(stocks):
    for key, value in sorted(stocks.iteritems(), reverse=True, key=lambda kvt: float(kvt[1][3][1])):
        print "%s\t%s\t%s\t%s" %( key,
                                  color1(stocks[key][3][0],stocks[key][4]),
                                  color2("",stocks[key][3][1],"%"),
                                  color2("(",stocks[key][3][2]," "+stocks[key][2]+")"))
    print ""
    end_time = time()
    sleep(sleeptime+start_time-end_time)
