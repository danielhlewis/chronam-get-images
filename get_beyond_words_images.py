import json
import sys
import urllib
import requests
from PIL import Image, ImageFont, ImageDraw, ImageEnhance


# first we open the beyond words data (cached in beyond_words_data for reproducability, but can be found here:  http://beyondwords.labs.loc.gov/data)
with open('beyond_words_data/beyond_words.txt') as f:
    bw = json.load(f)

# grabs the data containing the list of annotated images
contents = bw["data"]

# quick print of stats
print("Total # of images: " + str(len(contents)))

# create log for storing pages that don't download
log = open("build_manifest_log.txt", "a")


ct = 1

# now, we iterate through annotation and grab the image using requests
for annotation in contents:

    # pull off the values we need
    id = annotation["id"]
    location = annotation["location"]["standard"]
    annoation_region = annotation["region"]
    im_width = annotation["width"]
    im_height = annotation["height"]

    # sets coordinates of annotation region
    x1 = int(annotation_region["x"])
    x2 = x1 + int(annotation_region["width"])
    y1 = int(annotation_region["y"])
    y2 = y1 + int(annotation_region["height"])

    # constructs filepath for downloaded image
    destination = "beyond_words_data/extracted/" + str(id) + ".jpg"
    label_path = "beyond_words_data/labels/" + str(id) + ".jpg"

    print(region)
    print(width)
    print(height)

    # here, we try to pull down the image (if the request isn't stale)
    try:
        r = requests.get(location, stream=True)
        # makes sure the request passed:
        if r.status_code == 200:
            with open(destination, 'wb') as f:
                f.write(r.content)

        sys.stdout.write("\rProcessed Image "+str(ct)+"/"+str(len(contents))+"           ")
        sys.stdout.flush()

    except:
        log.write("Download failed: " + str(location) + "\n")

    # now, we construct the label image
    label = PIL.Image.new(mode = "RGB", size = (width, height))
    label  = ImageDraw.Draw(label)
    label.rectangle(((0, 0), (width, height)), fill="black")
    label.rectangle((x1, y1), (x2, y2)), fill="red")

    source_img.save(out_file, "PNG")



    ct += 1

    sys.exit()
