from collector import WayCollector
from pathlib import Path
import msgpack
import multiprocessing

def process_file(input_file):
    collector = WayCollector()
    collector.verbose = True
    collector.roads = ['motorway','trunk','primary','secondary','tertiary','unclassified','residential','motorway_link','trunk_link','primary_link','secondary_link']

    collection = list(collector.parse(str(input_file)))
    output_path = Path('msgPackFiles', f'{input_file.name}.msgpack')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'wb') as f:
        msgpack.pack(collection, f, use_bin_type=True)


if __name__ == '__main__':
    input_files = list(Path('osmData').glob('*.pbf'))

    with multiprocessing.Pool() as pool:
        pool.map(process_file, input_files)
