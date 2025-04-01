

if __name__ == "__main__":
    import msgpack
    import sys
    from io import BytesIO, StringIO
    from collector import WayCollector

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

    print()
    print()
    print(len(collections))

    input("WAITING FOR INPUT")

    ## Filter on things
    f_out.seek(0)
    f_in = BytesIO(f_out.read())

    from curvature.post_processors.filter_out_ways_with_tag import FilterOutWaysWithTag
    # unpacker = msgpack.Unpacker(f_in, use_list=True)
    post_processor = FilterOutWaysWithTag()
    post_processor.tag = 'surface'
    post_processor.values = 'unpaved,compacted,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil'.split(',')
    post_processor.filter_out_ways_missing_tag = False
    iterable = post_processor.process(collections)

    f_out = BytesIO()
    for collection in iterable:
        print(collection)
        f_out.write(msgpack.packb(collection, use_bin_type=True))

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


    output_file = open('output.kml','wb')
    kml.head(sys.stdout)
    unpacker = msgpack.Unpacker(f_out, use_list=True)
    for collection in unpacker:
        kml.write_collection(output_file, collection)

    kml.foot(sys.stdout)
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