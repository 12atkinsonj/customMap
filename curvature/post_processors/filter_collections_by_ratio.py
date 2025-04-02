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
