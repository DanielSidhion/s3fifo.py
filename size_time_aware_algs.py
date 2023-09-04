class FIFOTimed:
    def __init__(self, size):
        self.max_size = size
        self.fifo = []
        self.table = {}
        self.sizes = {}
        self.rem_size = size
        self.hits = self.misses = 0

    def get(self, key, curr_timestamp, expiry_ts, item_size):
        if key in self.table:
            self.hits += 1
            self.table[key] = max(self.table[key], expiry_ts)
        else:
            self.misses += 1
            size_to_clear = item_size - self.rem_size
            if size_to_clear > 0:
                i = 0
                while i < len(self.fifo):
                    k = self.fifo[i]
                    
                    if self.table[k] <= curr_timestamp:
                        # We can clear this item, not used anymore.
                        size_to_clear -= self.sizes[k]
                        self.rem_size += self.sizes[k]
                        del self.sizes[k]
                        del self.table[k]
                        self.fifo.pop(i)

                        if size_to_clear <= 0:
                            break
                        # We popped from the list, so there's no need to increment i.
                        continue
                    i += 1
                
                if size_to_clear > 0:
                    print(f'current timestamp is {curr_timestamp}')
                    print(f'rem_size={self.rem_size}, trying to add item with size={item_size}')
                    print(f'fifo state: {self.fifo}')
                    print(f'table state: {self.table}')
                    raise Exception("Can't make space in the cache for this item!")
            
            self.table[key] = expiry_ts
            self.rem_size -= item_size
            self.sizes[key] = item_size
            self.fifo.append(key)
