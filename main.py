from processRoads import processRoads

configs = []

# configs.append(
#     {
#     'file_name':'default.kml',
#     'split_straight_len':1609,
#     'speed_min':30,
#     'total_curve_min':300,
#     'curve_ratio_min':0.1,
#     'curve_ratio_or': False,
#     'total_length_min':2414
#     })

configs.append({
    'file_name':'extraCurvy.kml',
    'split_straight_len':1609,
    'speed_min':30,
    'total_curve_min':2500,
    'curve_ratio_min':0.35,
    'curve_ratio_or': True,
    'total_length_min':2414
    })

configs.append({
    'file_name':'fastDefault.kml',
    'split_straight_len':1609,
    'speed_min':45,
    'total_curve_min':300,
    'curve_ratio_min':0.1,
    'curve_ratio_or': False,
    'total_length_min':2414
    })

for config in configs:
    print(f"Processing: {config['file_name']} ...")
    processRoads(config)