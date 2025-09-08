from processRoads import processRoads
import re

def getPolygon():
    with open ('polygonFilter', 'r') as f:
        s = str(f.read())
    coords = re.search('<coordinates>([0-9 \\t\\n.\-,.]*)<',s).group(1)
    coords = re.sub('[\\t\\n]','',coords)
    coords = coords.strip()

    coords = coords.split(' ')
    output = []
    for coord in coords:
        tmp = coord.split(',')[:2]
        tmpc = (tmp[0], tmp[1])
        output.append(tmpc)

    return output

configs = []

configs.append({
    'file_name':'CurvyRoads.kml',
    'split_straight_len':1610, #1 mile
    'speed_min':30,
    'total_curve_min':1200,
    'curve_ratio_min':0.22,
    'curve_ratio_or': True,
    'total_length_min':1610, #1 mile
    'top_n':2000,
    'center_lat': 39.815556, 
    'center_long': -74.823611,
    # 'center_lat': 39.4538888889, 
    # 'center_long': -76.9577777778,
    'loc_radius': 130000,
    'polygon_filter': getPolygon()
    })



# {
#     'file_name':'CurvyRoads.kml',
#     'split_straight_len':1610, #1 mile
#     'speed_min':28,
#     'total_curve_min':1000,
#     'curve_ratio_min':0.2,
#     'curve_ratio_or': True,
#     'total_length_min':1610, #1 mile
#     'top_n':2000,
#     'center_lat': 39.815556, 
#     'center_long': -74.823611,
#     'loc_radius': 130000,
#     }

# configs.append({
#     'file_name':'CurvyRoads_Long.kml',
#     'split_straight_len':1610, #1mi
#     'speed_min':28,
#     'total_curve_min':1500,
#     'curve_ratio_min':0.2,
#     'curve_ratio_or': True,
#     'total_length_min':4828, #3 miles
#     'top_n':2000,
#     'center_lat': 40.524438, 
#     'center_long': -75.461417,
#     'loc_radius': 130000,
#     })

# configs.append({
#     'file_name':'CurvyRoads_Fast.kml',
#     'split_straight_len':1610, #1 mile
#     'speed_min':35,
#     'total_curve_min':1000,
#     'curve_ratio_min':0.2,
#     'curve_ratio_or': True,
#     'total_length_min':1610, #1 mile
#     'top_n':2000,
#     'center_lat': 40.524438, 
#     'center_long': -75.461417,
#     'loc_radius': 130000,
#     })

from_scratch = True
for config in configs:
    print(f"Processing: {config['file_name']} ...")
    processRoads(config, from_scratch=from_scratch)
    from_scratch = False