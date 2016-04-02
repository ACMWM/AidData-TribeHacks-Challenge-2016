import overpy

api = overpy.Overpass()

longitude = -1.6030642544
latitude  = 6.6762723
search_width = 0.015

# base case: look for baba yada kumani stadium
s = latitude  - search_width
w = longitude - search_width
n = latitude  + search_width
e = longitude + search_width

query_string = ("way" + \
        "[\"leisure\"~\"stadium|pitch|sports_centre\"]" + \
        "(%s,%s,%s,%s);" + \
        "(._;>;);" + \
    "out;") % (s, w, n, e)

print(query_string)

result = api.query(query_string)

for way in result.ways:
    print("Name: %s" % way.tags.get("name", "n/a"))
    print("  Nodes:")
    for node in way.nodes:
        print("    Lat: %f, Lon: %f" % (node.lat, node.lon))
