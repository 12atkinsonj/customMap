# -*- coding: UTF-8 -*-
import argparse
import shapely

class FilterCollectionsByPolygon(object):
    def __init__(self, polygon):
        self.polygon = shapely.Polygon(polygon)

    def process(self, iterable):
        for collection in iterable:
            within = False
            # Use an already-summed curvature value if it exists on the collection.
            for way in collection['ways']:
                for coord in way['coords']:
                    point = shapely.Point(coord[1], coord[0])

                    if point.within(self.polygon):
                        within = True
                        break
                
                if within:
                    break

            if within:
                yield(collection)

