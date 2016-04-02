import os
import overpy
import csv

api = overpy.Overpass()
# f = open("maps_api_key", 'r')
# maps_api_key = f.readline()

"""
Tag descriptors are stored as maps
"""
tags = {}
tags["Stadium"] = ["leisure",  "stadium|pitch|sports_centre"]
tags["Dam"]     = ["waterway", "dam"]

base_url = "\t\thttp://maps.google.com/maps?"

def main():
    with open(input("Enter csv filename:\n")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        # Read the header of the csv file if you need it
        headers = next(reader)

        # Go through all the locations in the csv file
        for location in reader:
            # Query OSM Overpass API for nearby objects matching the query
            find_possible_sat_imgs(location)

def find_possible_sat_imgs(location):
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

    query_string = ("way" + \
            "[\"%s\"~\"%s\"]" + \
            "(%s,%s,%s,%s);" + \
            "(._;>;);" + \
        "out;") % (category, regex, s, w, n, e)

    result = api.query(query_string)

    for way in result.ways:
        nodes = way.nodes

        # Find the midpoint of the discovered object
        lats = sorted([float(node.lat) for node in nodes])
        lngs = sorted([float(node.lon) for node in nodes])
        [mid_lat, mid_lng] = [sum(x)/len(x) for x in [lats, lngs]]

        print("\tPossible %s at:" % loc[2])
        sat_url = base_url + "z=10&t=k&q=loc:%f+%f" % (mid_lat, mid_lng)
        print(sat_url)

main()
