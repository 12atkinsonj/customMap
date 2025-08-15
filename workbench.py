from collector import WayCollector
from pathlib import Path
import msgpack

collector = WayCollector()
collector.verbose = True
collector.roads = ['motorway','trunk','primary','secondary','tertiary','unclassified','residential','motorway_link','trunk_link','primary_link','secondary_link']

for input_file in Path('osmData').glob('*.pbf'):
    collection = list(collector.parse(str(input_file)))

    with open(Path('msgPackFiles',f'{input_file.name}.msgpack'), 'wb') as f:
        msgpack.pack(collection, f, use_bin_type=True)