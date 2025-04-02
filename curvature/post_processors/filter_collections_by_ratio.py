# -*- coding: UTF-8 -*-
import argparse

class FilterCollectionsByRatio(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def process(self, iterable):
        for collection in iterable:
            # Use an already-summed curvature value if it exists on the collection.
            ratio = collection['ratio']
            
            if self.min is not None:
                if ratio < self.min:
                    continue
            if self.max is not None:
                if ratio > self.max:
                    continue
            yield(collection)

class FilterCollectionsByRatioOrCurves(object):
    def __init__(self, min_r=0, min_c=0):
        self.min_r = min_r
        self.min_c = min_c

    def process(self, iterable):
        for collection in iterable:

            # Use an already-summed curvature value if it exists on the collection.
            
            ratio = collection['ratio']
            curvature = collection['curvature']
            if ratio < self.min_r and curvature < self.min_c:
                    continue
            yield(collection)