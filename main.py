

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
        collector.roads = ['motorway','trunk','primary','secondary','tertiary','unclassified','residential','service','motorway_link','trunk_link','primary_link','secondary_link','service']

        input_file = 'pennsylvania-latest.osm.pbf'

        ## READ the file and build the initial colleciton

        # f = open('output.msgpack','wb')
        f_out = BytesIO()
        collections = []
        def output(collection):
            collections.append(collection)
        # start parsing
        collector.parse(input_file, output)


        with open('data.msgpack', 'wb') as f:
            msgpack.pack(collections, f, use_bin_type=True)
    else:
        with open("data.msgpack", "rb") as f:
            byte_data = f.read()
            collections = msgpack.unpackb(byte_data, strict_map_key=False)

    from curvature.post_processors.filter_out_ways_with_tag import FilterOutWaysWithTag
    surface_filter = FilterOutWaysWithTag()
    surface_filter.tag = 'surface'
    surface_filter.values = 'unpaved,compacted,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil'.split(',')
    surface_filter.filter_out_ways_missing_tag = False

    service_filter = FilterOutWaysWithTag()
    service_filter.tag = 'service'
    service_filter.values = 'driveway,parking_aisle,drive-through,parking,bus,emergency_access,alley'.split(',')
    service_filter.filter_out_ways_missing_tag = False

    area_filter = FilterOutWaysWithTag()
    area_filter.tag = 'area'
    area_filter.values = ['yes']
    area_filter.filter_out_ways_missing_tag = False

    collections = surface_filter.process(collections)
    collections = service_filter.process(collections)
    collections = area_filter.process(collections)

    from curvature.post_processors.add_segments import AddSegments
    from curvature.post_processors.add_segment_length_and_radius import AddSegmentLengthAndRadius
    from curvature.post_processors.add_segment_curvature import AddSegmentCurvature

    add_segments = AddSegments()
    add_segment_len = AddSegmentLengthAndRadius()
    add_segment_curve = AddSegmentCurvature()

    collections = add_segments.process(collections)
    collections = add_segment_len.process(collections)
    collections = add_segment_curve.process(collections)


    from curvature.post_processors.roll_up_length import RollUpLength
    from curvature.post_processors.roll_up_curvature import RollUpCurvature

    roll_up_len = RollUpLength()
    roll_up_curvature = RollUpCurvature()

    collections = roll_up_len.process(collections)
    collections = roll_up_curvature.process(collections)


    from curvature.post_processors.filter_collections_by_curvature import FilterCollectionsByCurvature
    filter_curves = FilterCollectionsByCurvature(min=1600)
    collections = filter_curves.process(collections)

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
    """
 $script_path/curvature-collect --highway_types 'motorway,trunk,primary,secondary,tertiary,unclassified,residential,service,motorway_link,trunk_link,primary_link,secondary_link,service' $verbose $input_file \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag surface --values 'unpaved,compacted,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag service --values 'driveway,parking_aisle,drive-through,parking,bus,emergency_access,alley' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag area --values 'yes' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag golf --values 'cartpath' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag access --values 'no' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag vehicle --values 'no' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag motor_vehicle --values 'no' \
      | $script_path/curvature-pp filter_out_ways --match 'And(TagEmpty("name"), TagEmpty("ref"), TagEquals("highway", "residential"), TagEquals("tiger:reviewed", "no"))' \
      | $script_path/curvature-pp filter_out_ways --match 'And(TagEquals("highway", "raceway"), TagEquals("sport", "motocross"))' \
      | $script_path/curvature-pp filter_out_ways --match 'And(TagEquals("highway", "service"), Or(TagEquals("access", "private"), TagEquals("motor_vehicle", "private"), TagEquals("vehicle", "private")))' \
      | $script_path/curvature-pp add_segments \
      | $script_path/curvature-pp add_segment_length_and_radius \
      | $script_path/curvature-pp add_segment_curvature \
      | $script_path/curvature-pp filter_segment_deflections \
      | $script_path/curvature-pp squash_curvature_for_tagged_ways --tag junction --values 'roundabout,circular' \
      | $script_path/curvature-pp squash_curvature_for_tagged_ways --tag traffic_calming \
      | $script_path/curvature-pp squash_curvature_for_ways --match 'TagAndValueRegex("^parking:lane:(both|left|right)", "parallel|diagonal|perpendicular|marked")' \
      | $script_path/curvature-pp squash_curvature_for_ways --match 'TagAndValueRegex("^parking:lane:(both|left|right):(parallel|diagonal|perpendicular)", "^(on_street|on_kerb|half_on_kerb|painted_area_only)$")' \
      | $script_path/curvature-pp squash_curvature_near_way_tag_change --tag junction --only-values 'roundabout,circular' --distance 30 \
      | $script_path/curvature-pp squash_curvature_near_way_tag_change --tag oneway --ignored-values 'no' --distance 30 \
      | $script_path/curvature-pp squash_curvature_near_tagged_nodes --tag highway --values 'stop,give_way,traffic_signals,crossing,mini_roundabout,traffic_calming' --distance 30 \
      | $script_path/curvature-pp squash_curvature_near_tagged_nodes --tag traffic_calming --distance 30 \
      | $script_path/curvature-pp squash_curvature_near_tagged_nodes --tag barrier --distance 30 \
      | $script_path/curvature-pp split_collections_on_straight_segments --length 2414 \
      | $script_path/curvature-pp roll_up_length \
      | $script_path/curvature-pp roll_up_curvature \
      | $script_path/curvature-pp filter_collections_by_curvature --min 300 \
      | $script_path/curvature-pp sort_collections_by_sum --key curvature --direction DESC \
      > $temp_dir/$filename.msgpack
    """