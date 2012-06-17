from optparse import OptionParser
from time import strftime, sleep
from json import loads
from Queue import LifoQueue, Queue
from threading import Thread, Lock 
import sys

#for testing threading lib
from random import randrange

TIMEFORMAT = 	"%H:%M:%S"
LISTURL	=		"http://api.twitpic.com/2/users/show.json?username=%s&page=%s"
DOWNLOADURL =	"http://twitpic.com/show/full/%s"
TESTJSON = 		'[{"id":"19049088","short_id":"bcadc","user_id":"662","source":"site","message":"I Fight Dragons hat Humor!","views":"30","width":"1038","height":"732","size":"119244","type":"png","status_id":null,"in_reply_to_status_id":null,"in_reply_to_user_id":null,"location":"","timestamp":"2009-07-23 17:03:24","application":null,"user":null,"video":null,"number_of_comments":"0","faces":null,"comments":null,"events":null,"tags":null},{"id":"18471504","short_id":"azwpc","user_id":"662","source":"api","message":"Heute ","views":"50","width":"2048","height":"1536","size":"687013","type":"jpg","status_id":null,"in_reply_to_status_id":null,"in_reply_to_user_id":null,"location":"","timestamp":"2009-07-20 12:57:45","application":null,"user":null,"video":null,"number_of_comments":"0","faces":null,"comments":null,"events":null,"tags":null},{"id":"18456693","short_id":"azl9x","user_id":"662","source":"api","message":"Im #CIS. #lol","views":"45","width":"2048","height":"1536","size":"621374","type":"jpg","status_id":null,"in_reply_to_status_id":null,"in_reply_to_user_id":null,"location":"","timestamp":"2009-07-20 09:09:37","application":null,"user":null,"video":null,"number_of_comments":"0","faces":null,"comments":null,"events":null,"tags":null},{"id":"19049088","short_id":"bcadc","user_id":"662","source":"site","message":"I Fight Dragons hat Humor!","views":"30","width":"1038","height":"732","size":"119244","type":"png","status_id":null,"in_reply_to_status_id":null,"in_reply_to_user_id":null,"location":"","timestamp":"2009-07-23 17:03:24","application":null,"user":null,"video":null,"number_of_comments":"0","faces":null,"comments":null,"events":null,"tags":null},{"id":"19049088","short_id":"bcadc","user_id":"662","source":"site","message":"I Fight Dragons hat Humor!","views":"30","width":"1038","height":"732","size":"119244","type":"png","status_id":null,"in_reply_to_status_id":null,"in_reply_to_user_id":null,"location":"","timestamp":"2009-07-23 17:03:24","application":null,"user":null,"video":null,"number_of_comments":"0","faces":null,"comments":null,"events":null,"tags":null}]'
# json.loads only interprets a single json-object!
# need to add [ before and ] after the downloaded string

def logger(lvl, msg):
	# TODO races!!! add some synchronisation or get some pipe to do the trick
	logLock.acquire()
	if options.verbose and (lvl < options.loglevel):
		print "%s\t%s" % (strftime(TIMEFORMAT), msg)
	logLock.release()

def getJSONForUser(user):
	# download from: DOWNLOADURL % (user, page-iterator)
	# meanwhile just some copy-and-paste for debug reasons
	return TESTJSON 

def getDataFromJSON(jsonstring):
	return loads(jsonstring)

def getLinksFromData(data):
	result = []
	for pic in data:
		result.append(pic[u'short_id'])
	return result

def download():
	#TODO
	sleep(dice())
	logger(3,"removing\t%s" % fifo.get())
	fifo.task_done()

def dice(num=1,sides=6):
    return sum(randrange(sides)+1 for die in range(num))

parser = OptionParser()
parser.add_option("-d", "--directory", 	dest="dir", default=".",
	help="specify an output directory")
parser.add_option("-q", "--quiet",	dest="verbose", action="store_false",
	default=True, help="suppress all output")
parser.add_option("-l", "--loglevel",	dest="loglevel", default=1,
	help="specify the output's loudness")
parser.add_option("-t","--threadcount", dest="threadcount", default=10,
	help="specify how many threads should be used for downloading images")

(options, args) = parser.parse_args()
fifo = Queue(int(options.threadcount))
logLock = Lock()

if (len(args) == 0):
	logger(0,"Plesase specify a Username")
	sys.exit(1)

for user in args:
	logger(0,"Downloading all Pictures from %s" % user)

	pic_ids = getLinksFromData(getDataFromJSON(getJSONForUser(user)))
	print pic_ids

	for (i, pic_id) in enumerate(pic_ids):
		#the following will block until a free slot is available
		fifo.put(i)
		downloadthread = Thread(target=download)
		logger(3,"starting thread\t%s" % (i+1))
		downloadthread.start()
