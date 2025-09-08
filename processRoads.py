import msgpack
from pathlib import Path
from collector import WayCollector
from itertools import chain

def collectionGenerator():
    for collection_file in Path('msgPackFiles').glob('*.msgpack'):
        
        if collection_file.name not in (
            'pennsylvania-latest.osm.pbf.msgpack',
            'new-jersey-latest.osm.pbf.msgpack',
            'delaware-latest.osm.pbf.msgpack',
            'maryland-latest.osm.pbf.msgpack',
            ):
            continue

        print(f"Processing {collection_file.name}")
        with open(collection_file, "rb") as f:
            byte_data = f.read()
            collections = msgpack.unpackb(byte_data, strict_map_key=False)
            for collection in collections:
                yield collection
            del collections


def processRoads(config = {}, from_scratch=False):

    file_name = config['file_name']
    split_straight_len = config['split_straight_len']
    speed_min = config['speed_min']
    total_curve_min = config['total_curve_min']
    curve_ratio_min = config['curve_ratio_min']
    total_length_min = config['total_length_min']
    curve_ratio_or = config['curve_ratio_or']
    top_n = config['top_n']
    center_lat = config['center_lat']
    center_long = config['center_long']
    loc_radius = config['loc_radius']
    poly = config.get('polygon_filter',None)
       
    collections = collectionGenerator()
    
    from curvature.post_processors.filter_collections_by_polygon import FilterCollectionsByPolygon
    polygon_filter = FilterCollectionsByPolygon(polygon=poly)
    collections = polygon_filter.process(collections)

    from curvature.post_processors.filter_out_ways_with_tag import FilterOutWaysWithTag
    surface_filter = FilterOutWaysWithTag(tag='surface', values='unpaved,compacted,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil'.split(','))
    service_filter = FilterOutWaysWithTag(tag='service', values='driveway,parking_aisle,drive-through,parking,bus,emergency_access,alley'.split(','))
    area_filter = FilterOutWaysWithTag(tag='area', values=['yes'])
    golf_filter = FilterOutWaysWithTag(tag='golf', values=['cartpath'])
    access_filter = FilterOutWaysWithTag(tag='access', values=['no'])
    vehicle_filter = FilterOutWaysWithTag(tag='vehicle', values=['no'])
    motor_vehicle_filter = FilterOutWaysWithTag(tag='motor_vehicle', values=['no'])

    # collections = chain(*collections)
    collections = surface_filter.process(collections)
    collections = service_filter.process(collections)
    collections = area_filter.process(collections)
    collections = golf_filter.process(collections)
    collections = access_filter.process(collections)
    collections = vehicle_filter.process(collections)
    collections = motor_vehicle_filter.process(collections)

    from curvature.post_processors.add_segments import AddSegments
    from curvature.post_processors.add_segment_length_and_radius import AddSegmentLengthAndRadius
    from curvature.post_processors.add_segment_curvature import AddSegmentCurvature
    from curvature.post_processors.filter_segment_deflections import FilterSegmentDeflections
    
    
    add_segments = AddSegments()
    add_segment_len = AddSegmentLengthAndRadius()
    add_segment_curve = AddSegmentCurvature()
    filter_deflections = FilterSegmentDeflections()

    collections = add_segments.process(collections)
    collections = add_segment_len.process(collections)
    collections = add_segment_curve.process(collections)
    collections = filter_deflections.process(collections)
   
    from curvature.post_processors.squash_curvature_near_tagged_nodes import SquashCurvatureNearTaggedNodes
    from curvature.post_processors.squash_curvature_for_tagged_ways import SquashCurvatureForTaggedWays
    from curvature.post_processors.squash_curvature_near_way_tag_change import SquashCurvatureNearWayTagChange
    
    squash_curves = SquashCurvatureNearTaggedNodes(tag='highway', distance=30, values=['stop', 'give_way', 'traffic_signals'])
    squash_tagged_ways = SquashCurvatureForTaggedWays(tag='junction', values=['roundabout', 'circular'])
    squash_change_tagged_ways = SquashCurvatureNearWayTagChange(tag='junction', distance=30, only_values=['roundabout', 'circular'])
    
    collections = squash_curves.process(collections)
    collections = squash_tagged_ways.process(collections)
    collections = squash_change_tagged_ways.process(collections)

    from curvature.post_processors.split_collections_on_straight_segments import SplitCollectionsOnStraightSegments
    split_straights = SplitCollectionsOnStraightSegments(straight_segment_split_threshold=split_straight_len)
    collections = split_straights.process(collections)

    from curvature.post_processors.roll_up_length import RollUpLength
    from curvature.post_processors.roll_up_curvature import RollUpCurvature
    from curvature.post_processors.normalize_curvature_by_length import NormalizeCurvatureByLength

    roll_up_len = RollUpLength()
    roll_up_curvature = RollUpCurvature()
    length_norm = NormalizeCurvatureByLength()

    collections = roll_up_len.process(collections)
    collections = roll_up_curvature.process(collections)
    collections = length_norm.process(collections)

    from curvature.post_processors.filter_collections_by_speed import FilterCollectionsBySpeed
    speed_filter = FilterCollectionsBySpeed(avg=speed_min)
    collections = speed_filter.process(collections)


    if curve_ratio_or:
        from curvature.post_processors.filter_collections_by_ratio import FilterCollectionsByRatioOrCurves
        filter_curves_or = FilterCollectionsByRatioOrCurves(min_r=curve_ratio_min, min_c=total_curve_min)
        collections = filter_curves_or.process(collections)
    else:
        from curvature.post_processors.filter_collections_by_ratio import FilterCollectionsByRatio
        from curvature.post_processors.filter_collections_by_curvature import FilterCollectionsByCurvature
       
        filter_curves = FilterCollectionsByCurvature(min=total_curve_min)
        filter_ratio = FilterCollectionsByRatio(min=curve_ratio_min)
       
        collections = filter_curves.process(collections)
        collections = filter_ratio.process(collections)

    collections = polygon_filter.process(collections)

    from curvature.post_processors.filter_collections_by_length import FilterCollectionsByLength
    filter_length = FilterCollectionsByLength(min=total_length_min)
    collections = filter_length.process(collections)

    # from curvature.post_processors.filter_collections_by_location import FilterCollectionsByLocation
    # location_filter = FilterCollectionsByLocation(lat=center_lat, long=center_long, radius=loc_radius)
    # collections = location_filter.process(collections)

    from curvature.post_processors.sort_collections_by_sum import SortCollectionsBySum
    sorter = SortCollectionsBySum(key='curvature', reverse=True)
    collections = sorter.process(collections)


    from curvature.post_processors.head import Head
    top_n_filter = Head(top_n)
    collections = top_n_filter.process(collections)

    
    ## Write the file to .kmz
    from curvature.output import SingleColorKmlOutput

    units = 'mi'
    min_curvature = 300
    max_curvature = 5000
    assumed_paved_highways = 'motorway,motorway_link,trunk,trunk_link,primary,primary_link,secondary,secondary_link'
    paved_surfaces = 'paved,asphalt,concrete,concrete:lanes,concrete:plates,metal,wood,cobblestone'
    
    kml = SingleColorKmlOutput(
        units=units, 
        min_curvature=min_curvature, 
        max_curvature=max_curvature, 
        assumed_paved_highways=assumed_paved_highways,
        paved_surfaces=paved_surfaces,
        name=file_name[:-4]
    )


    output_file = open(file_name,'w')
    kml.head(output_file)
    for collection in collections:
        kml.write_collection(output_file, collection)
    kml.foot(output_file)
    output_file.close()