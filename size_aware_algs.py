from collections import deque
from dataclasses import dataclass
from typing import Hashable

class FIFOSized:
    def __init__(self, size):
        self.max_size = size
        self.fifo = deque()
        self.table = {}
        self.rem_size = size
        self.hits = self.misses = 0

    def get(self, key, item_size):
        if key in self.table:
            self.hits += 1
        else:
            self.misses += 1
            size_to_clear = item_size - self.rem_size
            while size_to_clear > 0:
                if len(self.fifo) == 0:
                    raise Exception('Item added is bigger than the entire cache!')

                k = self.fifo.popleft()
                size_to_clear -= self.table[k]
                self.rem_size += self.table[k]
                del self.table[k]
            
            self.rem_size -= item_size
            self.table[key] = item_size
            self.fifo.append(key)

@dataclass(slots=True)
class S3FIFOItem:
    key: Hashable
    size: float
    freq: int = 0

class S3FIFONaiveSized:
    """
    This is an adaptation of the S3FIFO code implemented by Colin Caine in s3fifo.py. Original code Copyright Colin Caine 2023. MIT License.
    Adaptations were made to work with items of reasonably arbitrary size (there will be floating point issues if sizes are either too large, too small, or deal with a lot of fractional digits).
    Finally, this code won't actually cache any values, or return any values on a get operation. It's here purely to test how well it performs under certain conditions compared to other code.
    """
    def __init__(self, size, max_pct_cached):
        assert size * max_pct_cached > 0
        target_len_s = size * max_pct_cached
        self.target_len_m = size - target_len_s
        self.size = size

        # Stats
        self.hits = self.hit_ghosts = self.misses = 0

        # hashtable of key => Item for each item in S, M, G
        self.table = {}
        # FIFOs of Items
        self.S = deque()
        self.s_size = 0
        self.M = deque()
        self.m_size = 0
        self.G = deque()
        self.g_size = 0

    def get(self, key, item_size):
        item = None
        if key in self.table:
            item = self.table[key]
            if item.freq < 0:
                # Cache miss, item in G.
                # (Items entering G have freq set to -1).
                self.hit_ghosts += 1
                self.misses += 1

                # Re-cache the value and reset freq (import to do this before ensure_free!).
                item.freq = 0

                self.ensure_free()
                self.insertM(item)

                # We don't need to delete from G, that will happen automatically as we add values to G.
            else:
                # Cache hit! Update freq.
                self.hits += 1
                item.freq = min(item.freq + 1, 3)
        else:
            # Cache miss, unseen or forgotten key.
            self.misses += 1

            item = S3FIFOItem(key, item_size)
            self.table[key] = item

            # Insert into small fifo.
            self.ensure_free()
            self.insertS(item)

    def insertM(self, item):
        item.freq = 0
        self.M.appendleft(item)
        self.m_size += item.size

    def insertS(self, item):
        self.S.appendleft(item)
        self.s_size += item.size

    def insertG(self, new_item):
        # Evict items from G if it will be full. Items that have not been adopted into another queue are completely removed from the cache.
        while self.g_size + new_item.size >= self.target_len_m:
            tail_item = self.G.pop()
            self.g_size -= tail_item.size
            if tail_item.freq < 0:
                del self.table[tail_item.key]

        new_item.freq = -1
        self.G.appendleft(new_item)
        self.g_size += new_item.size

    def ensure_free(self):
        'Ensure there is at least one location free for a new item'
        while self.s_size + self.m_size >= self.size:
            if self.m_size >= self.target_len_m or self.s_size == 0:
                self.evictM()
            else:
                # We need the outer while loop because if every item in S is eligible for promotion to M, then evictS() will not evict anything to G and we will need to call evictM().
                self.evictS()

    def evictM(self):
        # Evict something, completely removing it from the cache.
        while self.m_size > 0:
            tail_item = self.M.pop()
            if tail_item.freq > 0:
                # Reinsert.
                tail_item.freq -= 1
                self.M.appendleft(tail_item)
            else:
                # Evict. Item may still be in G.
                self.m_size -= tail_item.size
                del self.table[tail_item.key]
                return
        assert False, 'Unreachable!'

    def evictS(self):
        # Promote items into M until we find an item we can demote to G or run out of items.
        while self.s_size > 0:
            tail_item = self.S.pop()
            self.s_size -= tail_item.size
            if tail_item.freq > 0:
                self.insertM(tail_item)
            else:
                self.insertG(tail_item)
                return