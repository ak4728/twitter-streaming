# -*- coding: utf-8 -*-
import logging
import logging.handlers
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from dateutil import parser
from django.utils.encoding import smart_str
from dateutil.parser import parse
import MySQLdb
from datetime import timedelta
from datetime import datetime
import schedule
import time
import datetime
import sys
import webbrowser
import random


# Go to http://dev.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key="put_consumer_key_here"
consumer_secret="put_consumer_secret_here"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token="put_access_token_here"
access_token_secret="put_access_token_secret_here"

### Config ###
locs = [-75,39,-73,41]  #This is the part you enter yoru bounding box lat lon values
nsecs=random.randint(60,63) # number of seconds the code will sleep when there is an error
streamTimeout = 30.0 # Stream timeout if there is something wrong

# Create your MySQL schema and connect to database, ex: mysql> SET PASSWORD FOR 'root'@'localhost' = PASSWORD('newpwd');
db=MySQLdb.connect(host='localhost', user='root', passwd='', db='twitter') 
db.set_character_set('utf8')

Coords = dict()
Place = dict()
PlaceCoords = dict()
XY = []
curr=db.cursor()

monthV = time.strftime("%B")

# Creates a database for the month
# You can use create table if not exists here
try:
    ex = "CREATE TABLE twitter_od_"+monthV+" (t_id varchar(45) NOT NULL, tweet varchar(255) DEFAULT NULL, created_at datetime DEFAULT NULL, latitude float(12,8) DEFAULT NULL, longitude float(12,8) DEFAULT NULL, screen_name varchar(45) DEFAULT NULL,   `mention` varchar(45) DEFAULT NULL, reply varchar(45) DEFAULT NULL, retweet_count varchar(45) DEFAULT NULL, place varchar(45) DEFAULT NULL,PRIMARY KEY (t_id), UNIQUE KEY t_id_UNIQUE (t_id) ) ENGINE=InnoDB DEFAULT CHARSET=latin1" 
    curr.execute(ex)
    db.commit()
    print 'created'
except:
    print 'already exist'

class StdOutListener(StreamListener):
                """ A listener handles tweets that are the received from the stream. 
                This is a basic listener that inserts tweets into MySQLdb.
                """
                def on_status(self, status):
                                #print "Tweet Text: ",status.text
                                # Text to string conversion
                                text1 = status.text
                                text2 = str(text1.replace("'", "").encode("ascii", "ignore"))
                                text = "'"+text2+"'"

                                # Tweet ID to string conversion
                                tid1 =  str(status.id)
                                tid = "'"+tid1+"'"

                                # Date to string conversion
                                tempdate = str(status.created_at)
                                dt = parse(tempdate).strftime("%Y-%m-%d %H:%M:%S")
                                dt1 = parser.parse(dt)
                                date1 = str(dt1 - timedelta(hours = 5))
                                date = "'"+date1+"'"


                                #user_mentions
                                try:
                                    mention = str(status.entities['user_mentions'][0].id)
                                    ment = "'"+mention+"'"
                                except:
                                    ment = "'"+str(0)+"'"
                                    pass


                                #replies
                                if (status.in_reply_to_user_id_str) == None:
                                    repl = "'"+str(0)+"'"
                                else:
                                    reply = str((status.in_reply_to_user_id_str).encode("ascii", "ignore"))
                                    repl = "'"+reply+"'"


                                #retweet
                                retweetcount = str(status.retweet_count)
                                rtwtcnt = "'"+retweetcount+"'"


                                #place
                                if (status.user.location) == None:
                                    place = '0'
                                    plc = '0'
                                else:
                                    place = str((status.user.location).encode("ascii", "ignore")).translate(None, "'")
                                    plc = "'"+place+"'"

                                #coordinates
                                try:
                                    Coords.update(status.coordinates)
                                    XY = (Coords.get('coordinates'))  #Place the coordinates values into a list 'XY'
                                    #print "X: ", XY[0]
                                    #print "Y: ", XY[1]
                                except:
                                    #Often times users opt into 'place' which is neighborhood size polygon
                                    #Calculate center of polygon
                                    XY = [0,0]

                                    #print "X: ", XY[0]
                                    #print "Y: ", XY[1] 
                                    pass

                                #Lat Lon to String conversion
                                X1 = XY[0]
                                Y1 = XY[1]
                                X = "'"+str(X1)+"'"
                                Y = "'"+str(Y1)+"'"
                                screen_name1 = status.author.screen_name
                                username = "'"+str(screen_name1)+"'"


                                if Y1 >= 40.570686 and Y1 <= 40.699652:
                                    if X1 >= -74.022733 and X1 <=-73.697263 :
                                        print tid1
                                        curr.execute("INSERT INTO brooklyn (t_id, tweet, created_at, latitude, longitude, screen_name, mention, reply, retweet_count, place) \
                                           VALUES ("+tid+","+text+","+date+","+Y+","+X+","+username+","+ment+","+repl+","+rtwtcnt+","+plc+")")
                                        db.commit()
                      


def main():
    l = StdOutListener()    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l, timeout=streamTimeout)
    #Only records 'locations' OR 'tracks', NOT 'tracks (keywords) with locations'
    while True:
        try:
            # Call tweepy's userstream method 
            # Use either locations or track, not both
            stream.filter(locations=locs, async=False)
            ##These coordinates are approximate bounding box around USA
            #stream.filter(track=['obama'])## This will feed the stream all mentions of 'keyword' 
            break
        except Exception, e:
             # Abnormal exit: Reconnect
             print 'In the sleeping mode.',e
             time.sleep(nsecs)            

if __name__ == '__main__':
    main()