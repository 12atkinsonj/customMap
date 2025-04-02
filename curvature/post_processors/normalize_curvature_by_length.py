# -*- coding: UTF-8 -*-
import argparse
import re

def extract_speed(speedLimit):
    return int(re.sub('[^0-9]','',str(speedLimit)))

class NormalizeCurvatureByLength(object):

    def process(self, iterable):
        for collection in iterable:
            if collection['curvature'] < 1e-3:
                ratio = 0
            else:
                ratio = collection['curvature']/collection['length']
                collection['ratio'] = ratio
                
            yield(collection)
