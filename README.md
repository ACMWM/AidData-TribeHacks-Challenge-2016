### The AidData “Skytruthiness” Challenge

One of AidData’s flagship data products is the Tracking Underreported Financial Flows (TUFF)
Chinese Aid to Africa dataset. The data is collected using a method which relies heavily on third-party
reporting of aid projects from China to African nations. One of the harder problems to solve is whether
or not these aid projects actually have occurred or are occurring. There are two potential ways to verify
that the projects have occurred. The first is **ground truthing**: actually sending someone to verify the
project occurred. Obviously, this can be expensive! The second is **sky truthing**: using satellite imagery
and remote sensing to see if we can pick up the signature of these development projects without putting
boots on the ground. Say for example, we have found some indication using TUFF that a stadium was
built in Uganda, we have shown we can skytruth these stadiums using Google Earth. Read more here:
http://aiddata.org/blog/the-skys-the-limit-using-satellite-imagery-to-track-development-financeprojects-in-africa

However it remains a tricky and perhaps labor intensive problem! This Challenge is all about
attempting to automate this process.

##### THE CHALLENGE:

Given the following items:

1. A set of latitude and longitude pairs which represent some Stadiums in Ghana;
2. A set of latitude and longitude pairs which represent some Dams in Ghana;
3. An export of Open Street Map (OSM) data of Ghana in Shapefile, sqlite and PBF formats (available at: ftp://ftp.aiddata.wm.edu/tribehacks);
4. the Google Maps API (https://developers.google.com/maps/)

Create an application which:

A) Takes each of the data points in (1) above and finds the nearest object in the OSM data. For example if the row is:

5.5515, 0.1919, Stadium

It would find the nearest Stadium in the OSM file for Ghana for that latitude and longitude. Then..

B) Use the location of the nearest object of found in (A), Save the most detailed satellite image from Google Maps. For example above, it would be the Accra Sports Stadium, and your image would look something like:

https://www.google.com/maps/place/Accra+Sports+Stadium/@5.5514127,-0.1927612,454m/data=!3m1!1e3!4m5!1m2!2m1!1sstadium+ghana!3m1!1s0xfdf9085f7383c39:0x7c72cdef39372119

NOTE: We only want the satellite image! Not the screen capture of the Google Maps page. You should probably be using the Google Maps API to retrieve your satellite tiles.

C) Your final output should at minimum be a CSV with the original latitude, longitude, object type, as
well as three new columns: 1) the OSM node id of the nearest matching object, 2) distance in km of the nearest found matching OSM object and 3) the name of the saved image file of the satellite view of the object (please store the files in a single folder)

D) Please issue a pull-request to this repo with your solution (in a seperate folder). Winning entries must contain all code, contain build instructions and generally be nice to work with. Judging criteria are: completeness of solution, code quality, an innovation (feel free to add cool features we havent thought of).

##### BONUS POINTS

E) Extend your application to arbitrary object mappings. By this we mean, given a source file with one
object type in it, say railroads, ask the user which OSM tags map to that object types.

##### HINTS:

1) The stadium and dam object tags the source data maps to a very specific OSM tag.

###### Stadium:
http://wiki.openstreetmap.org/wiki/Tag:building%3Dstadium

###### Dam:
http://wiki.openstreetmap.org/wiki/Tag:waterway%3Ddam

###### Questions? Email Scott Stewart (sstewart@aiddata.org) or Alex Kappel (akappel@aiddata.org).
