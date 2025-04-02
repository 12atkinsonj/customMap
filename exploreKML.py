with open('output2.kml', 'r') as f:
    while True:
        str = f.read(1000)
        print(str)
        input()