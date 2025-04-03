# -*- coding: UTF-8 -*-
import argparse
import geopy
import geopy.distance

class FilterCollectionsByLocation(object):
    def __init__(self, lat=None, long=None, radius=1600):
        self.lat = lat
        self.long = long
        self.radius = radius

    def process(self, iterable):
        for collection in iterable:
            out_of_r = False
            # Use an already-summed curvature value if it exists on the collection.
            for way in collection['ways']:
                for coord in way['coords']:
                    dist = geopy.distance.geodesic((coord[0], coord[1]),(self.lat, self.long)).meters

                    if dist > self.radius:
                        out_of_r = True
                        break
                
            if out_of_r:
                continue

            yield(collection)

