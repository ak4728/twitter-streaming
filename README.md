# twitter-streaming
Collects data from Twitter Streaming API 


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
