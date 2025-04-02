# -*- coding: UTF-8 -*-
import argparse
import re

def extract_speed(speedLimit):
    try:
        speed = int(re.sub('[^0-9]','',str(speedLimit)))
    except:
        speed = 0
    return speed

class FilterCollectionsBySpeed(object):
    def __init__(self, min=None, max=None, avg=None):
        self.min = min
        self.max = max
        self.avg = avg

    def process(self, iterable):
        for collection in iterable:
            speeds = []
            maxspeed = 0
            minspeed = 999
            for way in collection['ways']:
                # Use an already-summed length value if it exists on the way.
                if 'maxspeed' in way['tags']:
                    maxspeed = max(extract_speed(way['tags']['maxspeed']), maxspeed)
                    minspeed = min(extract_speed(way['tags']['maxspeed']), minspeed)
                    speeds.append(extract_speed(way['tags']['maxspeed']))

            #if there were no speeds provided, set the min to 0
            if minspeed == 999:
                minspeed = 0

            if speeds:
                avgspeed = round(sum(speeds)/len(speeds),2)
            else:
                avgspeed = 0

            collection['avgspeed'] = avgspeed
            collection['maxspeed'] = maxspeed
            collection['minspeed'] = minspeed


            if self.avg is not None:
                if avgspeed < self.avg:
                    continue
            if self.min is not None:
                if maxspeed < self.min:
                    continue
            if self.max is not None:
                if minspeed > self.max:
                    continue

            yield(collection)
