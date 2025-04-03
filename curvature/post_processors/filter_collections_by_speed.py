# -*- coding: UTF-8 -*-
import argparse
import re

def extract_speed(speedLimit):
    try:
        speed = int(re.sub('[^0-9]','',str(speedLimit)))
    except:
        speed = 0
    return speed

speed_lookup = {
    'motorway':55,
    'trunk':55,
    'primary':45,
    'secondary':35,
    'tertiary':30,
    'residential':25
}

class FilterCollectionsBySpeed(object):
    def __init__(self, min=None, max=None, avg=None):
        self.min = min
        self.max = max
        self.avg = avg

    def process(self, iterable):
        for collection in iterable:
            speeds = []
            lengths = []
            maxspeed = 0
            minspeed = 999
            for way in collection['ways']:
                # Use an already-summed length value if it exists on the way.
                if 'maxspeed' in way['tags']:
                    way_speed = extract_speed(way['tags']['maxspeed'])
                
                elif 'highway' in way['tags']:
                    road_type = way['tags']['highway']
                    way_speed = speed_lookup.get(road_type, 0)
                
                else:
                    way_speed = 0

                maxspeed = max(way_speed, maxspeed)
                minspeed = min(way_speed, minspeed)
                speeds.append(way_speed)
                lengths.append(way['length'])

            #if there were no speeds provided, set the min to 0
            if minspeed == 999:
                minspeed = 0

            if speeds:
                weighted_speed = 0
                for s, l in zip (speeds, lengths):
                    weighted_speed += s*l
                
                avgspeed = round(weighted_speed/sum(lengths),2)
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
