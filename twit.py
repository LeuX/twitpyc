from optparse import OptionParser
from time import strftime, sleep
from json import loads
from Queue import LifoQueue, Queue
from threading import Thread, Lock, Semaphore 
from urllib2 import urlopen, HTTPError
from os import path
import sys

#for testing threading lib
from random import randrange

TIMEFORMAT = 	"%H:%M:%S"
LISTURL	=		"http://api.twitpic.com/2/users/show.json?username=%s&page=%s"
DOWNLOADURL =	"http://twitpic.com/show/full/%s"

def logger(lvl, msg):
	if options.verbose and (lvl <= int(options.loglevel)):
		logLock.acquire()
		print "%s\t%s" % (strftime(TIMEFORMAT), msg)
		logLock.release()

def getDataForUser(user):
	"""
	#TODO Debug
	return {"images":[{"short_id":"48r4y2"}]}
	"""
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

def getLinksFromData(data):
	return [img["short_id"] for img in data["images"]]

def download(link, outdir):
	def copyFile(src,dst):
		dst.write(src.read())

	src = urlopen(link)
	filename = path.join(options.outdir,link.split('/')[-1]+'.'+src.info().getsubtype())
	try:
		dst = open(filename, 'wb')
		logger(2,"saving to %s" % filename)
	except IOError:
		logger(0,"coudn't open "+filename+" for writing")
		exit(1)
	copyFile(src,dst)

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

parser = OptionParser()
parser.add_option("-d", "--directory", dest="outdir", default=".",	help="specify an output directory")
parser.add_option("-q", "--quiet", dest="verbose", action="store_false",default=True, help="suppress all output")
parser.add_option("-l", "--loglevel", dest="loglevel", default=1, help="specify the output's loudness")
parser.add_option("-t","--threadcount", dest="threadcount", default=10, help="specify how many threads should be used for downloading images")

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
