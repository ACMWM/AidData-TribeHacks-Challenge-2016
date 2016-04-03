import os
import overpy
import csv
import tkinter.filedialog
import urllib

from yattag import Doc

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
    img_data = get_imgs_of_ways(ways, obj_type, loc_num)

    # Get images of nodes, if there are any matching
    if len(ways) == 0:
        nodes = query_for_nodes(category, regex, s, w, n, e)
        img_data = get_imgs_of_nodes(nodes, obj_type, loc_num)

    generate_html(img_data, obj_type, latitude, longitude, loc_num)


def query_for_ways(category, regex, s, w, n, e):
    query_string = ("way" + \
            "[\"%s\"~\"%s\"]" + \
            "(%s,%s,%s,%s);" + \
            "(._;>;);" + \
        "out;") % (category, regex, s, w, n, e)
    # print(query_string)
    return api.query(query_string).ways


def query_for_nodes(category, regex, s, w, n, e):
    query_string = ("node" + \
            "[\"%s\"~\"%s\"]" + \
            "(%s,%s,%s,%s);" + \
        "out;") % (category, regex, s, w, n, e)
    return api.query(query_string).nodes


def get_imgs_of_ways(ways, obj_type, loc_num):
    way_img_data = []
    for way in ways:
        nodes = way.nodes
        coords = [[float(node.lat), float(node.lon)] for node in nodes]
        [sw, ne] = get_bounding_box(coords)
        # Find the midpoint of the discovered object
        lats = sorted([float(node.lat) for node in nodes])
        lngs = sorted([float(node.lon) for node in nodes])
        [mid_lat, mid_lng] = [sum(x)/len(x) for x in [lats, lngs]]
        way_img = get_img_box(sw, ne, obj_type, loc_num)
        way_img_data.append(way_img)
    return way_img_data


def get_imgs_of_nodes(nodes, obj_type, loc_num):
    node_img_data = []
    for node in nodes:
        [lat, lng] = [node.lat, node.lon]
        node_img = get_img(lat, lng, 10, obj_type, loc_num)
        node_img_data.append(node_img)
    return node_img_data


def get_img_box(sw, ne, obj_type, loc_num):
    print("  Possible %s at:" % obj_type)
    mid_lat = (sw[0] + ne[0])/2
    mid_lng = (sw[1] + ne[1])/2
    sat_url = base_url + "z=10&t=k&q=loc:%f+%f" % (mid_lat, mid_lng)
    # print(sat_url)

    img_folder = create_dir_if_necessary(obj_type)

    coord_string = ("%.4fx%.4f" % (mid_lat, mid_lng)).replace('.', ',')
    img_path = img_folder + "%s%d_%s.png" % (obj_type, loc_num, coord_string)
    print("    Downloading image of this %s to %s." % (obj_type, img_path))

    img_url = "https://maps.googleapis.com/maps/api/staticmap?" + \
        "maptype=satellite&size=1280x1024&visible=%f,%f&visible=%f,%f" % (sw[0], sw[1], ne[0], ne[1])
    # print(img_url)
    urllib.request.urlretrieve(img_url, img_path)

    return { "path": img_path, "link": sat_url, "lat": mid_lat,
        "lng": mid_lng }


def get_img(lat, lng, zoom, obj_type, loc_num):
    print("  Possible %s at:" % obj_type)
    sat_url = base_url + "z=10&t=k&q=loc:%f+%f" % (lat, lng)
    print(sat_url)

    img_folder = create_dir_if_necessary(obj_type)

    coord_string = ("%.4fx%.4f" % (lat, lng)).replace('.', ',')
    img_path = img_folder + "%s%d_%s.png" % (obj_type, loc_num, coord_string)
    print("    Downloading image of this %s to %s." % (obj_type, img_path))

    img_url = base_img_url + ("%f,%f" % (lat, lng))
    print(img_url)
    urllib.request.urlretrieve(img_url, img_path)

    return { "path": img_path, "link": sat_url, "lat": lat,
        "lng": lng }


def get_bounding_box(points):
    n = points[0][0]
    s = points[0][0]
    w = points[0][1]
    e = points[0][1]
    for p in points:
        if p[0] > n:
            n = p[0]
        if p[0] < s:
            s = p[0]
        if p[1] > e:
            e = p[1]
        if p[1] < w:
            w = p[1]

    return [[s,w], [n, e]]

def create_dir_if_necessary(obj_type):
    directory  = obj_type + "_images"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory + "/"


def generate_html(img_data, obj_type, lat, lng, loc_num):
    doc, tag, text = Doc().tagtext()

    with tag("html"):
        with tag("body"):
            with tag('h2'):
                text("%ss near (%f, %f)" % (obj_type, lat, lng))
            for img in img_data:
                with tag("a", href=img["link"], id="sat-img-container"):
                    doc.stag("img", src=img["path"])
                with tag("p"):
                    text("%s at (%f, %f)" % (obj_type, img["lat"], img["lng"]))

    html_to_write = doc.getvalue()

    with open("%s%d.html" % (obj_type, loc_num), "w") as f:
        f.write(html_to_write)


main()
