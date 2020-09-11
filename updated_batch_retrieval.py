from datetime import datetime
# from pgmagick import Image
import os
import sys
import requests
import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import time
import glob
from PIL import Image
import math



#This function creates a manifest containing the web urls of every jp2 newspaper page images from Chronicling America.
#It does this by first navigating to the html page that links to each of the batch folders, then scrubs
#through the html source code to acquire the names of each batch folder. Once batch folder names are acquired, the function navigates
#to each batch folder and loads up the manifest for that batch, retrieves the urls for the images from the manifest
#and appends the URLs to the full manifest file.
def buildFullManifest():

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
    log = open("build_manifest_log.txt", "a")

    # iterate through scraped URLs
    for j in listOfBatchURLS:  # can truncate for testing (e.g., [:10])

        openf = open("manifests/" + j[:-1] + ".txt", "a")

        count += 1
        sys.stdout.write("\rProcessing "+str(count)+"/"+str(length)+" batch manifests (current: "+j+")")
        sys.stdout.flush()

        # add time delay to prevent taking down site
        time.sleep(1.5)

        # header for request
        headers = {'User-Agent':'Mozilla/5.0'}

        # we open each manifest-sha1.txt file to extract the filepaths of the .jp2 images (each image is a scan of a page)
        try:
            # sets path for "manifest-sha1.txt"
            path = batchesURL+j+"manifest-sha1.txt"
            # load in the full URL (basepath + j)
            page = requests.get(path)
            soup = BeautifulSoup(page.text, "html.parser")

            # creates list for storing image paths
            fullDataPaths = []

            # split lines in .txt
            lines = str(soup).splitlines()

            # then parse each line (we want to grab each image filepath that is in .jp2 format)
            for line in lines:
                partialDataPath = line.split()
                if partialDataPath[1].endswith('.jp2') and partialDataPath[1].count('/') == 4:
                    fullDataPaths.append(j+partialDataPath[1]+'\n')
                    fullDataPaths.sort()

	    ##########

            openf.writelines(fullDataPaths)
            openf.close()

        # if the sha1 manifest file fails, try the md5 manifest file instead
        except Exception as e:

            try:
                # sets path for "manifest-md5.txt"
                path = batchesURL+j+"manifest-md5.txt"
                # load in the full URL (basepath + j)
                page = requests.get(path)
                soup = BeautifulSoup(page.text, "html.parser")

                # creates list for storing image paths
                fullDataPaths = []

                # split lines in .txt
                lines = str(soup).splitlines()

                # then parse each line (we want to grab each image filepath that is in .jp2 format)
                for line in lines:
                    partialDataPath = line.split()
                    if partialDataPath[1].endswith('.jp2') and partialDataPath[1].count('/') == 4:
                        fullDataPaths.append(j+partialDataPath[1]+'\n')
                        fullDataPaths.sort()

                openf.writelines(fullDataPaths)
                openf.close()

            except Exception as e2:

                print("Encountered an error with batch " + j + "\n")
                log.write("Batch " + j + " failed: \n")

    log.close()


## HANDLE THE FACT THAT THE MANIFES FILE DOESN'T WORK ANYMORE - REPLACED WITH SMALLER FILES


#This function, when given a begin year and an end year, will search through the full Manifest file
#and download all images within a year range. For images from a single year, the same year is used for both parameters.
#The images are downloaded to the following directory structure: data/FullPages/BatchLevel/IssueLevel/PageLevel
#This function also uses wget in order to download images, this is due to complications we ran into
#using urllib with the Library of Congress's server.
def getImages(startYear=1836, startMonth=1, startDay=1, endYear=datetime.now().year, endMonth=datetime.now().month, endDay=datetime.now().day, bool_jp2=True, bool_xml=True, bool_txt=True):
    Error404 = []
    imageCount = 0
    fullCount = 0

    workingDirectory = os.getcwd()

    log = open("build_manifest_log.txt", "a")

    # url prefix for fetching images
    batchesURL = "http://chroniclingamerica.loc.gov/data/batches/"

    # grabs all of the filepaths for text files that contain image filepaths to pull
    manifests = glob.glob('manifests/*.txt')

    for manifest_file in manifests:

        with open(manifest_file, "r") as masterManifest:

            # iterate through the files in the manifest
            for line in masterManifest:
                line = batchesURL + line
                lineList = line.split('/')

                # parses off date of publication
                imageYear = int(lineList[9][:4])
                imageMonth = int(lineList[9][4:6])
                imageDay = int(lineList[9][6:8])

                # checks whether the image falls within desired date range
                if imageYear >= int(startYear) and imageYear <= int(endYear):
                    if imageMonth >= int(startMonth) and imageMonth <= int(endMonth):
                        if imageDay >= int(startDay) and int(imageDay) <= int(endDay):
                            imageCount += 1


        # # uncomment just for count
        # continue

    for manifest_file in manifests:
        with open(manifest_file, "r") as masterManifest:
            previousLine = ""
            pageCount = 1            
            for line in masterManifest:
                line = batchesURL + line
                lineList = line.split('/')

                #used in construction of the image's filename.
                #ensures consistent naming since each issue of a newspaper shares the same base name
                if lineList[9] == previousLine:
                    pageCount += 1
                else:
                    pageCount = 1

                # parses off date of publication
                imageYear = int(lineList[9][:4])
                imageMonth = int(lineList[9][4:6])
                imageDay = int(lineList[9][6:8])

                # checks whether the image falls within desired date range
                if imageYear >= int(startYear) and imageYear <= int(endYear):
                    if imageMonth >= int(startMonth) and imageMonth <= int(endMonth):
                        if imageDay >= int(startDay) and int(imageDay) <= int(endDay):
                            fullCount += 1
                            imageURL = line.strip()

                            #constructs file and directory names for sorting purposes
                            batchName = lineList[5]
                            snNumber = lineList[7]
                            date = lineList[9][:4]+"-"+lineList[9][4:6]+"-"+lineList[9][6:8]
                            edition = lineList[9][-1:]
                            issueName = snNumber+"_"+date+"_ed-"+edition
                            imageName = issueName+"_seq-"+str(pageCount)+".jp2"

                            if not os.path.exists("data/FullPages/"+batchName):
                                os.makedirs("data/FullPages/"+batchName)
                            if not os.path.exists("data/FullPages/"+batchName+"/"+issueName):
                                os.makedirs("data/FullPages/"+batchName+"/"+issueName)

                            os.chdir("data/FullPages/"+batchName+"/"+issueName)
                            print(imageURL)

                            try:
                                if bool_jp2:

                                    if not os.path.isfile(imageName):

                                        # pulls image
                                        r = requests.get(imageURL, stream=True)
                                        # makes sure the request passed:
                                        if r.status_code == 200:
                                            with open(imageName, 'wb') as f:
                                                f.write(r.content)

                                if bool_xml:

                                    if not os.path.isfile(imageName.replace('.jp2', '.txt')):

                                        # pulls OCR XML
                                        r = requests.get(imageURL.replace('.jp2', '.xml'))
                                        # makes sure the request passed:
                                        if r.status_code == 200:
                                            with open(imageName.replace('.jp2', '.xml'), 'wb') as f:
                                                f.write(r.content)

                                if bool_txt:

                                    if not os.path.isfile(imageName.replace('.jp2', '.txt')):

                                        # pulls OCR TXT
                                        ## FOR .TXT file in OCR, we need to use the API url structure, not batch URL structure
                                        ocrURL = "https://chroniclingamerica.loc.gov/lccn/" + snNumber + "/" + date + "/ed-" + edition + "/seq-" + str(pageCount) + "/ocr.txt"
                                        r = requests.get(ocrURL)
                                        # makes sure the request passed:
                                        if r.status_code == 200:
                                            with open(imageName.replace('.jp2', '.txt'), 'wb') as f:
                                                f.write(r.content)

                                sys.stdout.write("\rProcessed Image "+str(fullCount)+"/"+str(imageCount)+"           ")
                                sys.stdout.flush()

                                os.chdir(workingDirectory)

                            except:
                                log.write("Download failed: " + str(imageURL) + "\n")

                previousLine = lineList[9]

    print("Files downloaded; check error logs for any failed downloads")
    print("Total # of pages within query range: " + str(imageCount))


#This function searches through the directory structure created in the getImages function
#and converts all jp2 images to the jpg format. If an image can't be converted, the function adds
#the filename to a list of broken images, and this list is presented at the end of the process.
def convertToJpg():
    workingDirectory = os.getcwd()
    # resampling scale
    resampling_scale = 6

    problemImages = []
    os.chdir("data/FullPages")
    batchLevel = os.listdir(os.getcwd())
    totalBatches = len(batchLevel)
    currentBatch = 0
    for i in batchLevel:
        currentBatch += 1
        if i == '.DS_Store' or '.xml' in i or '.txt' in i:
            continue
        os.chdir(i)
        issueLevel = os.listdir(os.getcwd())
        totalIssues = len(issueLevel)
        currentIssue = 0
        for j in issueLevel:
            currentIssue += 1
            if j == '.DS_Store':
                continue
            os.chdir(j)
            jp2Images = os.listdir(os.getcwd())
            totalImages = len(jp2Images)
            currentImage = 0
            for k in jp2Images:
                currentImage += 1
                try:
                    if k == '.DS_Store' or '.xml' in k or '.txt' in k:
                        continue
                    # convert jp2 to jpg
                    command = "mogrify -resize 100x100% -quality 100 -format jpg " + k
                    os.system(command)

                    # # sleep before re-sizing to make sure mogrify is executed
                    # time.sleep(1.0)

                    # # downsample the iamge using PIL
                    # jpg_filepath = k.replace(".jp2", ".jpg")
                    # im = Image.open(jpg_filepath)
                    # im = im.resize( (math.floor(im.size[0]/float(resampling_scale)),math.floor(im.size[1]/float(resampling_scale))), Image.ANTIALIAS)
                    # im.save(jpg_filepath)

                    #Status update on how many images have been processed
                    sys.stdout.write("\rConverted Batch: "+str(currentBatch)+"/"+str(totalBatches)+" Issue: "+str(currentIssue)+"/"+str(totalIssues)+" Image: "+str(currentImage)+"/"+str(totalImages)+"           ")
                    sys.stdout.flush()
                    #remove old jp2 image to conserve space, also only remove if conversion was successful
                    os.remove(k)
                except:
                    problemImages.append(str(k))
            os.chdir('..')
        os.chdir('..')
    os.chdir(workingDirectory)

    #end of process message
    if len(problemImages) > 0:
        print("These are images that could not be converted to jpg for some reason. Please check for corruption/ proper download.")
        print(problemImages)
    else:
        print("All images converted successfully")




def usage():
    print("Usage: python Batch_Retrieval.py [1 | 2 | 3] [YYYY] [MM] [DD] [YYYY] [MM] [DD] [True | False] [True | False] [True | False]")
    print("    1 - build manifest and get images")
    print("    2 - get images only")
    print("    3 - build manifest only")
    print("    YYYY - Year beginning and ending (may use same year for both)")
    print("    MM - Month beginning and ending")
    print("    DD - Day beginning and ending")
    print("    True | False  x 3 for keeping .jp2, .xml, .txt")

if len(sys.argv) == 1:
    usage()
elif sys.argv[1] == "1":
    print("Preparing to build manifest and get images")
    buildFullManifest()
    getImages(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], 'True' == sys.argv[8], 'True' == sys.argv[9], 'True' == sys.argv[10])
    convertToJpg()
elif sys.argv[1] == "2":
    print("Preparing to get images")
    getImages(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], 'True' == sys.argv[8], 'True' == sys.argv[9], 'True' == sys.argv[10])
    convertToJpg()
elif sys.argv[1] == "3":
    print("Preparing to build manifest")
    buildFullManifest()
