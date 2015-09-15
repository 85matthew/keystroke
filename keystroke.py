#!/usr/bin/python
# -*- coding: utf-8 -*-


from AppKit import NSApplication, NSApp, NSWorkspace
from Foundation import NSObject, NSLog, NSAppleScript
from Cocoa import NSEvent, NSKeyDownMask, NSLeftMouseUpMask
from PyObjCTools import AppHelper, Conversion
import keycode
import appscript
import string
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
import mozrepl
from uptime import uptime
from urlparse import urlparse, parse_qs
import psycopg2

class AppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, notification):
        mask1 = NSKeyDownMask
        mask2 = NSLeftMouseUpMask
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask1, handler)
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask2, handler)

def handler(event):

    #############
    #VARS
    #activeAppName
    global lastAppName
    global lastUrl
    global url
    global lastDomain
    #global domains
    #lastDomain = ""
    appTime = "0"
    bootTime = ""
    #incomingTimestamp# = ""
    global appStartedTimestamp
    #global queryValue
    queryValue = ""
    global lastQueryValue
    domain = None
    #############

    browserList = ["Google Chrome", "Safari", "Firefox", "Firefox Plugin Content (Shockwave Flash)"]
    browserSet = set(browserList)
    #appStartedTimestamp = ""

    try:
        incomingTimestamp = datetime.now()
        print "******* NEW EVENT ********************"
        activeAppName = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
	print "Active APP"
        print activeAppName
        
        print "Last APP = "
        print  lastAppName

	if activeAppName in browserSet:
            print "About to launch getURLData"
            url, domain, queryValue = getURLData(activeAppName)

            print "GOT QUERY VALUES"
            print url
            print domain
            print queryValue

        else:
             url = ""
             domain =""
             queryValue = ""


            ###Keyboard Input- keydown activity###
        if event.type() == 10:
            print "keyDown Event=" + event.characters()
            print "" 

            ###Mouse Click- Left Click up Mouse Input###
        if event.type() == 2:
            print "mouseUp Event"

	print activeAppName

        print type(activeAppName) , type(lastAppName)
        print activeAppName
        print lastAppName

        if activeAppName == lastAppName:
            print "No Change in Active App"

            if activeAppName in browserSet:
                print lastUrl
                if lastUrl:
                    print "lastUrl tested as TRUE"
                    print url
                    print lastUrl

                    if lastUrl != url:
                
                        #write DB here
                    
                        duration = printLogEntry(incomingTimestamp)
                        print "Writing to DB..."

                        user = "matt"
                        userType = "userType1"
                        tenant = "tenant1"

                        insertDB(appStartedTimestamp, incomingTimestamp, duration, activeAppName, lastAppName, user, userType, tenant, lastDomain, lastQueryValue)
                        appStartedTimestamp = incomingTimestamp
                    
            else:
                  print "NO APP CHANGE & NO URL FROM BROWSER"
                  url = ""
                  domain = ""
                  queryValue = ""



        elif lastAppName is None:
            print "lastAppName was set to NULL"
            #printLogEntry()
            lastAppName = activeAppName
            print lastAppName
            appStartedTimestamp = incomingTimestamp
            #lastUrl.append(url)
            
        else:
            
            duration = printLogEntry(incomingTimestamp)
            print "DURATION HIT"
            print duration
            user = "matt"
            userType = "userType1"
            tenant = "tenant1"
            print activeAppName
            print lastAppName
            print lastUrl
            print url
            print lastDomain
            print lastQueryValue

            insertDB(appStartedTimestamp, incomingTimestamp, duration, activeAppName, lastAppName, user, userType, tenant, lastDomain , lastQueryValue)
            appStartedTimestamp = incomingTimestamp


        


        #Rotate Settings
        #######
        #appStartedTimestamp = incomingTimestamp
        lastAppName = activeAppName
        activeAppName = ""
        print "DOMAIN: " + domain

        lastDomain = domain
        domain = ""
        print "Rotated last domain"
        lastUrl = url
        url = ""
        print "Rotated last url"
        print "QUERY VALUE: " + str(queryValue)
        lastQueryValue = queryValue
        queryValue = ""
        print "Rotated queryValue " 
        


    except KeyboardInterrupt:
	print "Something fucked up! Exception!!!"
        AppHelper.stopEventLoop()

def ensureUniqueInList(newList, oldList):
    length = len(oldList)

    if newList not in oldList:
        return True
    else:
        return False
    

def printLogEntry(incomingTimestamp):

    #duration = str((incomingTimestamp - appStartedTimestamp)).split(".")[0]
    print "###############"
    duration = (incomingTimestamp - appStartedTimestamp)
    duration_str = str(duration).split(".")[0]
    print duration
    

    print "********** TOTAL TIME **********"
    print incomingTimestamp
    print "The time now is: " + incomingTimestamp.strftime("%H:%M:%S")
    print lastAppName + " Start: " + appStartedTimestamp.strftime("%H:%M:%S")
    print lastAppName + " End: " + incomingTimestamp.strftime("%H:%M:%S")
    print lastAppName + " Duration: " + str(duration) + "\n"

    return duration



def getURLData(browserType):
    
    global url
    #global domains
    #global queryValues

    domain = ""
    queryValue = ""


    print "Starting getURLData Function"
    if browserType == "Google Chrome":
        out = NSAppleScript.alloc().initWithSource_("tell application \"Google Chrome\" to return URL of active tab of front window")
        urls = out.executeAndReturnError_(None)
        url = urls[0]
        url = url.stringValue()

    elif browserType == "Safari":
        out = NSAppleScript.alloc().initWithSource_("tell application \"Safari\" to return URL of front document")
        urls = out.executeAndReturnError_(None)
        url = urls[0]
        url =  url.stringValue()

    elif browserType == "Firefox" or browserType == "Firefox Plugin Content (Shockwave Flash)":
        repl = mozrepl.Mozrepl()
        url = repl.execute("gLastValidURLStr")
        print url
        print "THATs the NON hacked value"
	

    print "Got the URL \n" + url
 
    urlParsed = urlparse(url)
    print urlParsed

    domain = urlParsed.netloc
    print "Got the domain: " + domain
    
    
    ### Parse Search String ####

    print "Running the Parse Search String Section"

    if bool(parse_qs(urlParsed.query)) or bool(parse_qs(urlParsed.fragment)):
        print "The user did a search on Google or Bing"
   
        if domain == "google.com" or domain == "www.google.com": 
            try:
                print "google section"
                queryValue = parse_qs(urlParsed.fragment)['q']
                print queryValue
                print "JUST PRINTED QUERY VALUES"
            except KeyError:
                print "Not a valid google url search" 

        elif "bing.com" in domain:
    
            try:
                print "bing"
                queryValue = parse_qs(urlParsed.query)['q']
            except KeyError:
                print "Not a valid bing url search"

    

    print "This is the queryValue: " + str(queryValue)

    print "Made it to end of function- get url"
    #START HERE

    print "VALUES to RETURN:"
    print url
    print domain
    print queryValue

    return url, domain, queryValue

def insertDB(appStartedTimestamp, incomingTimestamp, duration, activeAppName, lastAppName, userid, userType, tenant, lastDomain, lastQueryValue):

    global url, lastUrl

    print "About to Write to DB...."
    print "got these"
    print appStartedTimestamp, incomingTimestamp, duration, lastAppName, userid, userType, tenant, lastDomain, lastQueryValue
    

    try:
        conn = psycopg2.connect("dbname='dev' user='postgres' host='localhost' password='matt22'")
    except psycopg2.Error as e:

        print "Unable to connect to the DB"
        pass

    try:
        
       # data = 'appStartedTimestamp, incomingTimestamp, duration, lastAppName, "matt", "userType1", "tenant1", url, domain, lastQueryValues'
        #data = (
        #    ('appStartedTimestamp', 'incomingTimestamp', 'duration', 'lastAppName', 'matt', 'userType1', 'tenant1', 'url', 'domain',\
        #     'queryValues')
        #)
       # SQLfields = '"StartTimeStamp", "EndTimeStamp", "Duration", "AppName", "UserID", "UserType", tenant, url, domain, "keywordsSearched"'
        #query = 'INSERT into "events" ("StartTimeStamp", "EndTimeStamp", "Duration","AppName", "UserID", "UserType",\
        #         "Tenant", "Url", "Domain", "KeywordsSearched") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        

        cur = conn.cursor()
        
        print "About to blow up- executing now"
        #cur.executemany(query, data)

        try:
            cur.execute('INSERT INTO "events" ("start_time_stamp", "end_time_stamp", "duration","app_name", "user_id", "user_type", "tenant", "url", "domain", "search_words") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (appStartedTimestamp, incomingTimestamp, duration, lastAppName, userid, userType, tenant, lastUrl, lastDomain, lastQueryValue))
            conn.commit()
            print "********* SUCCESSFULLY WROTE TO DB *********"
        except psycopg2.DatabaseError, e:
            
            if conn:
                conn.rollback()
            print 'Error %s' %e

        finally:
            print "Running the Finally Section"
            if conn:
                conn.close()
            #Rotate Settings
            #######
            #lastAppName = activeAppName
            #appStartedTimestamp = incomingTimestamp
            #lastUrl = url
            #lastDomain = domain

            print "SENDING THESE VALUES"
            print "********************"
            print appStartedTimestamp
            print incomingTimestamp
            print duration
            print lastAppName
            print "matt"
            print "userType1"
            print "tenant1"
            print lastUrl
            print lastDomain
            print lastQueryValue

            
        #cur.execute("""
        #               INSERT into "EventsTable" ("StartTimeStamp", "EndTimeStamp", "Duration",
        #               "AppName", "UserID", "UserType", "Tenant", "Url", "Domain", "KeywordsSearched")
        #               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),
        #               (appStartedTimestamp, incomingTimestamp, duration, lastAppName, "matt",
        #               "userType1", "tenant1", url, domain, queryValues) """)

       #cur.execute("""INSERT into "EventsTable" (SQLfields) VALUES (data)  """)
        #print cur.fetchall()
        conn.close()
    except psycopg2.Error as e:
        print "The query is fucked up"
        print 'Error %s' % e 
        pass


def main():

    global lastAppName
    global url
    global lastUrl
    global lastDomain
    #global queryValue
    global lastQueryValue
    global lastDomain


    lastAppName = None
    url = None
    lastUrl = None
    #queryValue = None
    lastQueryValue = None
    lastDomain = ""
    #domain = ""
    #queryValue = 

    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    AppHelper.runEventLoop()

if __name__ == '__main__':
    main()
