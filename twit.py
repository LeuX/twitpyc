from optparse import OptionParser
from time import strftime, sleep
from json import loads
from Queue import LifoQueue, Queue
from threading import Thread, Lock, Semaphore 
from urllib2 import urlopen, HTTPError
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
	if options.verbose and (lvl <= int(options.loglevel)):
		logLock.acquire()
		print "%s\t%s" % (strftime(TIMEFORMAT), msg)
		logLock.release()

def getDataForUser(user):
	def nextpage(i):
		try:
			restObj = urlopen(LISTURL % (user,i))
			return loads(restObj.read())
		except HTTPError:
			return None

	data = nextpage(1)
	i=2
	while True: 
		pageN=nextpage(i)
		if not pageN:
			break
		i+=1
		data["images"].extend(pageN["images"])

	#TODO no good style, should use exceptions when, eg, there is no such user.
	return data

#	print [img["short_id"] for img in data["images"]]
#	exit()

def getLinksFromData(data):
	return [img["short_id"] for img in data["images"]]

def download(link, outdir):
	sleep(dice()/10)

def downloadWorker(link, outdir):
	logger(2,"starting download of %s" % link)
	download(link, outdir)
	logger(2,"finished download of %s" % link)
	threadLock.release()

def threadedDownload(links, outdir):
	for link in links:
		threadLock.acquire()
		downloadthread = Thread(target=downloadWorker, args=(link, outdir))
		logger(3,"starting thread")
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
	pic_ids = getLinksFromData(getDataForUser(user))
	links = [DOWNLOADURL % pic_id for pic_id in pic_ids]
	threadedDownload(links, options.outdir)
