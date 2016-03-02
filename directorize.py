import io, json, os.path, urllib2, sys

defaultFileName = "./dataLinks.json"
defaultDirName = "./TablaFiles"

def loadFromFile(filename):
    with open(filename, "r") as infile:
        return json.load(infile)

def downloadFile(link, filename):
    fileDownloaded = urllib2.urlopen(link)
    with open(filename, "wb") as output:
        output.write(fileDownloaded.read())
        output.close()

def iterateDict(dictLinks):
    currDir = defaultDirName
    iterator = 0
    for key, value in dictLinks.iteritems():

        year = key.split("-")[-1].strip()
        dirName = currDir + "/" + year
        fileName = currDir + "/" + year + "/" + key + ".html"

        if not os.path.isdir(dirName):
            os.mkdir(dirName)

        if not os.path.isfile(fileName):
            downloadFile(value["link"], fileName)

        iterator += 1
        print "\rNumber of files written: %d/%d" % (iterator, len(dictLinks)),
        sys.stdout.flush()

def createEnclosingDir():
    if not os.path.isdir(defaultDirName):
            os.makedirs(defaultDirName)

if __name__ == "__main__":

    origDict = loadFromFile(defaultFileName)
    createEnclosingDir()
    iterateDict(origDict)
