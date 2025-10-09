from processRoads import processRoads
import re

def getPolygon(fileName):
    with open (fileName, 'r') as f:
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

configs.append(
    # {
    # 'file_name':'SouthEastPA.kml',
    # 'msg_pack_filters':['pennsylvania'],
    # 'split_straight_len':1610, #1 mile
    # 'speed_min':30,
    # 'total_curve_min':1200,
    # 'curve_ratio_min':0.22,
    # 'curve_ratio_or': True,
    # 'total_length_min':1610, #1 mile
    # 'top_n':3000,
    # 'polygon_filter': getPolygon('southEastPA')
    # },
    #    {
    # 'file_name':'Maryland.kml',
    # 'msg_pack_filters':['maryland'],
    # 'split_straight_len':1610, #1 mile
    # 'speed_min':30,
    # 'total_curve_min':1200,
    # 'curve_ratio_min':0.22,
    # 'curve_ratio_or': True,
    # 'total_length_min':1610, #1 mile
    # 'top_n':3000,
    # },
    #        {
    # 'file_name':'New Jersey.kml',
    # 'msg_pack_filters':['new-jersey'],
    # 'split_straight_len':1610, #1 mile
    # 'speed_min':30,
    # 'total_curve_min':1200,
    # 'curve_ratio_min':0.22,
    # 'curve_ratio_or': True,
    # 'total_length_min':1610, #1 mile
    # 'top_n':3000,
    # },
    # {
    # 'file_name':'Maine.kml',
    # 'msg_pack_filters':['maine'],
    # 'split_straight_len':1610, #1 mile
    # 'speed_min':30,
    # 'total_curve_min':1200,
    # 'curve_ratio_min':0.22,
    # 'curve_ratio_or': True,
    # 'total_length_min':1610, #1 mile
    # 'top_n':3000,
    # },
    # {
    # 'file_name':'Delaware.kml',
    # 'msg_pack_filters':['delaware'],
    # 'split_straight_len':1610, #1 mile
    # 'speed_min':30,
    # 'total_curve_min':700,
    # 'curve_ratio_min':0.22,
    # 'curve_ratio_or': True,
    # 'total_length_min':1610, #1 mile
    # 'top_n':3000,
    # },

    {
    'file_name':'experimental.kml',
    'msg_pack_filters':['pennsylvania'],
    'split_straight_len':800, #1 mile
    'speed_min':30,
    'total_curve_min':500,
    'curve_ratio_min':0.22,
    'curve_ratio_or': True,
    'total_length_min':1610, #1 mile
    'top_n':3000,
    'polygon_filter': getPolygon('southEastPA')
    },
    )



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