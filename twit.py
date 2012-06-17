from optparse import OptionParser
from time import strftime, sleep
from json import loads
from Queue import LifoQueue, Queue
from threading import Thread, Lock, Semaphore 
import sys

#for testing threading lib
from random import randrange

TIMEFORMAT = 	"%H:%M:%S"
LISTURL	=		"http://api.twitpic.com/2/users/show.json?username=%s&page=%s"
DOWNLOADURL =	"http://twitpic.com/show/full/%s"
TESTJSON = 		'[{"id":"19049088","short_id":"bcadc"},{"id":"18471504","short_id":"azwpc"},{"id":"18456693","short_id":"azl9x"},{"id":"19049088","short_id":"bcadc"},{"id":"19049088","short_id":"bcadc"},{"id":"19049088","short_id":"bcadc"},{"id":"19049088","short_id":"bcadc"}]'
# json.loads only interprets a single json-object!
# need to add [ before and ] after the downloaded string

def logger(lvl, msg):
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

def download(link, outdir):
	#TODO
	sleep(dice())

def downloadWorker(link, outdir):
	download(link, outdir)
	threadLock.release()

def threadedDownload(links, outdir):
	for link in links:
		threadLock.acquire()
		downloadthread = Thread(target=downloadWorker, args=(link, outdir))
		logger(3,"starting download of %s" % link)
		downloadthread.start()

def dice(num=1,sides=6):
    return sum(randrange(sides)+1 for die in range(num))

parser = OptionParser()
parser.add_option("-d", "--directory", 	dest="outdir", default=".",
	help="specify an output directory")
parser.add_option("-q", "--quiet",	dest="verbose", action="store_false",
	default=True, help="suppress all output")
parser.add_option("-l", "--loglevel",	dest="loglevel", default=1,
	help="specify the output's loudness")
parser.add_option("-t","--threadcount", dest="threadcount", default=10,
	help="specify how many threads should be used for downloading images")

(options, args) = parser.parse_args()
logLock = Lock()
threadLock = Semaphore(int(options.threadcount))

if (len(args) == 0):
	logger(0,"Plesase specify a Username")
	sys.exit(1)


for user in args:
	logger(0,"Downloading all Pictures from %s" % user)

	pic_ids = getLinksFromData(getDataFromJSON(getJSONForUser(user)))
	print pic_ids
	
	links = [DOWNLOADURL % pic_id for pic_id in pic_ids]

	threadedDownload(links, options.outdir)
