

if __name__ == "__main__":
    import msgpack
    import sys
    from io import BytesIO, StringIO
    from collector import WayCollector

    from_scratch = False
    
    if from_scratch:
        # Instantiate our collector
        collector = WayCollector()
        collector.verbose = True
        collector.roads = ['motorway','trunk','primary','secondary','tertiary','unclassified','residential','motorway_link','trunk_link','primary_link','secondary_link']

        input_files = ['pennsylvania-latest.osm.pbf','new-jersey-latest.osm.pbf']

        ## READ the file and build the initial colleciton

        # f = open('output.msgpack','wb')
        f_out = BytesIO()
        collections = []
        def output(collection):
            collections.append(collection)
        # start parsing
        for input_file in input_files:
            collector.parse(input_file, output)


        with open('data.msgpack', 'wb') as f:
            msgpack.pack(collections, f, use_bin_type=True)
    else:
        with open("data.msgpack", "rb") as f:
            byte_data = f.read()
            collections = msgpack.unpackb(byte_data, strict_map_key=False)

    from curvature.post_processors.filter_out_ways_with_tag import FilterOutWaysWithTag
    surface_filter = FilterOutWaysWithTag(tag='surface', values='unpaved,compacted,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil'.split(','))
    service_filter = FilterOutWaysWithTag(tag='service', values='driveway,parking_aisle,drive-through,parking,bus,emergency_access,alley'.split(','))
    area_filter = FilterOutWaysWithTag(tag='area', values=['yes'])
    golf_filter = FilterOutWaysWithTag(tag='golf', values=['cartpath'])
    access_filter = FilterOutWaysWithTag(tag='access', values=['no'])
    vehicle_filter = FilterOutWaysWithTag(tag='vehicle', values=['no'])
    motor_vehicle_filter = FilterOutWaysWithTag(tag='motor_vehicle', values=['no'])

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

    from curvature.post_processors.split_collections_on_straight_segments import SplitCollectionsOnStraightSegments
    split_straights = SplitCollectionsOnStraightSegments(straight_segment_split_threshold=1800)
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
    speed_filter = FilterCollectionsBySpeed(min=0)
    collections = speed_filter.process(collections)

    from curvature.post_processors.filter_collections_by_curvature import FilterCollectionsByCurvature
    filter_curves = FilterCollectionsByCurvature(min=600)
    collections = filter_curves.process(collections)

    from curvature.post_processors.filter_collections_by_ratio import FilterCollectionsByRatio
    filter_curves = FilterCollectionsByRatio(min=.2)
    collections = filter_curves.process(collections)

    from curvature.post_processors.filter_collections_by_length import FilterCollectionsByLength
    filter_length = FilterCollectionsByLength(min=1610)
    collections = filter_length.process(collections)

    from curvature.post_processors.sort_collections_by_sum import SortCollectionsBySum
    sorter = SortCollectionsBySum(key='curvature', reverse=True)
    collections = sorter.process(collections)


    ## Write the file to .kmz
    from curvature.output import SingleColorKmlOutput

    units = 'mi'
    min_curvature = 500
    max_curvature = 4000
    assumed_paved_highways = 'motorway,motorway_link,trunk,trunk_link,primary,primary_link,secondary,secondary_link'
    paved_surfaces = 'paved,asphalt,concrete,concrete:lanes,concrete:plates,metal,wood,cobblestone'
    
    kml = SingleColorKmlOutput(
        units=units, 
        min_curvature=min_curvature, 
        max_curvature=max_curvature, 
        assumed_paved_highways=assumed_paved_highways,
        paved_surfaces=paved_surfaces,
    )


    output_file = open('output2.kml','w')
    kml.head(output_file)
    for collection in collections:
        kml.write_collection(output_file, collection)

    kml.foot(output_file)
    output_file.close()