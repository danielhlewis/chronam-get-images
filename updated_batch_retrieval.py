from datetime import datetime
# from pgmagick import Image
import os
import sys
import requests
import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


manifest_file = "Master_Manifest.txt"

#This function creates a manifest containing the web urls of every jp2 newspaper page images from Chronicling America.
#It does this by first navigating to the html page that links to each of the batch folders, then scrubs
#through the html source code to acquire the names of each batch folder. Once batch folder names are acquired, the function navigates
#to each batch folder and loads up the manifest for that batch, retrieves the urls for the images from the manifest
#and appends the URLs to the full manifest file.
def buildFullManifest():
    # remove existing manifest file in order to prevent appending to it
    if os.path.exists(manifest_file):
        print("Deleted " + manifest_file + " and generating new one")
        os.remove(manifest_file)
    print("Getting batch urls")
    batchesURL = "http://chroniclingamerica.loc.gov/data/batches/"

    # Ben's code for reading webpage
    # urllib requests were not being processed ("urllib.error.HTTPError: HTTP Error 403: Forbidden")
    # so switched to using BeautifulSoup
    # https://stackoverflow.com/questions/1080411/retrieve-links-from-web-page-using-python-and-beautifulsoup
    headers = {'User-Agent':'Mozilla/5.0'}
    page = requests.get(batchesURL)
    soup = BeautifulSoup(page.text, "html.parser")

    # list of URLs of newspaper info
    listOfBatchURLS = []
    print("finding names")

    # iterate through all of the hrefs to find the links
    for link in soup.find_all('a', href=True):
        # skip over two paths (return to parent directory and other random file)
        if link['href'] == '../' or link['href'] == '.keep':
            continue
        listOfBatchURLS.append(link['href'])

    # prints the total number of links
    print("Number of links found: " +str(len(listOfBatchURLS)))

    length = len(listOfBatchURLS)
    count = 0
    print("starting processing")
    openf = open(manifest_file, "a")
    log = open("build_manifest_log.txt", "a")

    # iterate through scraped URLs
    for j in listOfBatchURLS[:1]:
        count += 1
        sys.stdout.write("\rProcessing "+str(count)+"/"+str(length)+" batch manifests (current: "+j+")")
        sys.stdout.flush()

        headers = {'User-Agent':'Mozilla/5.0'}

        try:
            # sets path for "manifest-md5.txt"
            path = batchesURL+j+"manifest-md5.txt"
            # load in the full URL (basepath + j)
            page = requests.get(path)
            soup = BeautifulSoup(page.text, "html.parser")

            # split lines
            lines = str(soup).splitlines()

            fullDataPaths = []

            # then parse each line
            for line in lines:
                partialDataPath = line.split()
                print(partialDataPath)
                if partialDataPath[1].endswith('.jp2') and partialDataPath[1].count('/') == 4:
                    fullDataPaths.append(j+partialDataPath[1]+'\n')
                    fullDataPaths.sort()

        except:
            print("PROBLEM")

        # try to open sha1 manifest file, but if it isn't there, then try md5 file instead
        try:
            socket = urllib2.urlopen(batchesurl+j+"manifest-md5.txt")
            print(socket)
            sys.exit()
        except:
            print("HELP")

        # except err:
        #     if err.code == 404 or err.code == 503:
        #         try:
        #             socket = urllib2.urlopen(j+"manifest-md5.txt")
        #         except e:
        #             print("Error HTTP: "+ str(e.code))
        #             print("This is bad the manifest for batch "+j+" could not be acquired!!!\n")
        #             log.write("Batch " + j + " failed: " + str(e.code) + "\n")
        #     else:
        #         print("Encountered an error when accessing the url: " + str(err.code) + "\n")
        #         log.write("Batch " + j + "failed: " + str(err.code) + "\n")
        # except Exception as e:
        #     print("Error: " + str(e))
        #     print("Unable to make manifest for batch " + j + "\n")
        #     log.write("Batch " + j + " failed: " + str(e) + "\n")
        # try:
        #     manifest = socket.readlines()
        #     socket.close()
        #     fullDataPaths = []
        #     for k in manifest:
        #         partialDataPath = k.split()
        #         if partialDataPath[1].endswith('.jp2') and partialDataPath[1].count('/') == 4:
        #             fullDataPaths.append(j+partialDataPath[1]+'\n')
        #             fullDataPaths.sort()
        #
        #     openf.writelines(fullDataPaths)
        # except Exception as e:
        #     print("Encountered an error with batch " + j + " : "+ str(e) + "\n")
        #     log.write("Batch " + j + " failed: " + str(e) + "\n")
    openf.close()
    log.close()


def usage():
    print("Usage: python Batch_Retrieval.py [1 | 2 | 3] [YYYY] [YYYY]")
    print("    1 - build manifest and get images")
    print("    2 - get images only")
    print("    3 - build manifest only")
    print("    YYYY - Year beginning and ending (may use same year for both)")
    print("Examples:")
    print("    ./Batch_Retrieval.py 1 1938 1938")
    print("    ./Batch_Retrieval.py 3")

if len(sys.argv) == 1:
    usage()
elif sys.argv[1] == "1":
    print("Preparing to build manifest and get images")
    buildFullManifest()
    getImages(sys.argv[2], sys.argv[3])
    convertToJpg()
elif sys.argv[1] == "2":
    print("Preparing to get images")
    getImages(sys.argv[2], sys.argv[3])
    convertToJpg()
elif sys.argv[1] == "3":
    print("Preparing to build manifest")
    buildFullManifest()
