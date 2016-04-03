import os
import overpy
import csv
import tkinter.filedialog
import urllib

api = overpy.Overpass()
MAPS_API_KEY = None

with open("maps_api_key", 'r') as f:
    MAPS_API_KEY = f.readline().strip()

if MAPS_API_KEY is None:
    print("No Google Maps API key found. Please get one at \n\t" + \
          "https://developers.google.com/maps/documentation/static-maps/\n" + \
          "then place it in a file named maps_api_key")
    exit()


"""
Read in tags from tags.csv
"""
tags = None
with open("tags.csv", 'r') as csvfile:
    tags = {}
    reader = csv.reader(csvfile, delimiter=',')
    headers = next(reader)

    for tag_set in reader:
        tags[tag_set[0]] = [tag_set[1], tag_set[2]]

if tags is None:
    print("No tags file provided, exiting.")
    exit()

base_url = "    http://maps.google.com/maps?"
base_img_url = "https://maps.googleapis.com/maps/api/staticmap?" + \
    "maptype=satellite&zoom=18&size=1280x1024&key=" + MAPS_API_KEY + "&center="

# Get the CSV file we want to use
csv_filepath = tkinter.filedialog.askopenfilename(initialdir=os.getcwd())



def main():
    with open(csv_filepath) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')

        # Read the header of the csv file if you need it
        headers = next(reader)

        loc_num = 0 # Tracks the row number of the csv file for img file writing
        # Go through all the locations in the csv file
        for location in reader:
            # Query OSM Overpass API for nearby objects matching the query
            find_possible_sat_imgs(location, loc_num)
            loc_num += 1


def find_possible_sat_imgs(location, loc_num):
    # Clean the input
    loc = [location[i].strip() for i in range(len(location))]

    latitude  = float(loc[0])
    longitude = float(loc[1])
    [category, regex] = tags[loc[2]]

    # The width of the square we're searching in (units are lat/lng degrees)
    search_width = 0.015

    print("Look for %ss at (%f, %f):" % (loc[2], latitude, longitude))
    # base case: look for baba yada kumani stadium
    s = latitude  - search_width
    w = longitude - search_width
    n = latitude  + search_width
    e = longitude + search_width

    obj_type = loc[2]

    # Get images of ways, if there are any matching
    ways = query_for_ways(category, regex, s, w, n, e)
    get_imgs_of_ways(ways, obj_type, loc_num)

    # Get images of nodes, if there are any matching
    if len(ways) == 0:
        nodes = query_for_nodes(category, regex, s, w, n, e)
        get_imgs_of_nodes(nodes, obj_type, loc_num)

def query_for_ways(category, regex, s, w, n, e):
    query_string = ("way" + \
            "[\"%s\"~\"%s\"]" + \
            "(%s,%s,%s,%s);" + \
            "(._;>;);" + \
        "out;") % (category, regex, s, w, n, e)
    return api.query(query_string).ways


def query_for_nodes(category, regex, s, w, n, e):
    query_string = ("node" + \
            "[\"%s\"~\"%s\"]" + \
            "(%s,%s,%s,%s);" + \
        "out;") % (category, regex, s, w, n, e)
    return api.query(query_string).nodes


def get_imgs_of_ways(ways, obj_type, loc_num):
    for way in ways:
        nodes = way.nodes

        # Find the midpoint of the discovered object
        lats = sorted([float(node.lat) for node in nodes])
        lngs = sorted([float(node.lon) for node in nodes])
        [mid_lat, mid_lng] = [sum(x)/len(x) for x in [lats, lngs]]
        get_img(mid_lat, mid_lng, 10, obj_type, loc_num)

def get_imgs_of_nodes(nodes, obj_type, loc_num):
    for node in nodes:
        [lat, lng] = [node.lat, node.lon]
        get_img(lat, lng, 10, obj_type, loc_num)

def get_img(lat, lng, zoom, obj_type, loc_num):
    print("  Possible %s at:" % obj_type)
    sat_url = base_url + "z=10&t=k&q=loc:%f+%f" % (lat, lng)
    print(sat_url)

    img_folder = create_dir_if_necessary(obj_type)

    coord_string = ("%.4fx%.4f" % (lat, lng)).replace('.', ',')
    img_path = img_folder + "%s%d_%s.png" % (obj_type, loc_num, coord_string)
    print("    Downloading image of this %s to %s." % (obj_type, img_path))

    img_url = base_img_url + ("%f,%f" % (lat, lng))

    urllib.request.urlretrieve(img_url, img_path)

def create_dir_if_necessary(obj_type):
    directory  = obj_type + "_images"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory + "/"

main()
