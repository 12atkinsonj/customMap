

class CustomIter:
    def __init__(self):
        self.stop = False
        self.index = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.stop:
            raise StopIteration
        
        if self.index > 10:
            raise StopIteration
        
        self.index += 1
        return self.index
    
for i in CustomIter():
    print(i)
        
