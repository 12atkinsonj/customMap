with open ('polygonFilter', 'r') as f:
    s = str(f.read())

print(s)

import re

coords = re.search('<coordinates>([0-9 \\t\\n.\-,.]*)<',s).group(1)
coords = re.sub('[\\t\\n]','',coords)
coords = coords.strip()

coords = coords.split(' ')
print(coords)
output = []
for coord in coords:
    tmp = coord.split(',')[:2]
    print(tmp)
    tmpc = (tmp[0], tmp[1])
    output.append(tmpc)

print(output)