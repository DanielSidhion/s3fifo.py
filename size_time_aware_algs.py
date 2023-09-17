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

from collections import deque
from dataclasses import dataclass
from typing import Hashable

@dataclass(slots=True)
class S3FIFOItem:
    key: Hashable
    expiry_ts: float
    size: float
    freq: int = 0

class S3FIFONaiveTimed:
    """
    This is an adaptation of the S3FIFO code implemented by Colin Caine in s3fifo.py. Original code Copyright Colin Caine 2023. MIT License.
    Adaptations were made to work with items of reasonably arbitrary size (there will be floating point issues if sizes are either too large, too small, or deal with a lot of fractional digits).
    Adaptations were also made to work with items that can't be expired until a certain timestamp. This implementation is called "naive" because that was the first idea I had when thinking of how to adapt it: if an item would be evicted from the cache, we also check if it's already expired. If it is, we evict the item. If it's not, we forcibly keep the item in the cache until it expires.
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

    def get(self, key, curr_timestamp, expiry_ts, item_size):
        """
        expiry_ts is the earliest timestamp at which we're allowed to expire the item.
        curr_timestamp is the current timestamp as noticed by whatever code is calling us (we might be under simulation and advancing in time way faster than in reality).
        """
        item = None
        if key in self.table:
            item = self.table[key]
            if item.freq < 0:
                # Cache miss, item in G.
                # (Items entering G have freq set to -1).
                self.hit_ghosts += 1
                self.misses += 1

                # Re-cache the value and reset freq (import to do this before ensure_free!).
                item.expiry_ts = expiry_ts
                item.freq = 0

                self.ensure_free(curr_timestamp)
                self.insertM(item)

                # We don't need to delete from G, that will happen automatically as we add values to G.
            else:
                # Cache hit! Update freq and the expiry timestamp if it's longer than the current one.
                self.hits += 1
                item.freq = min(item.freq + 1, 3)
                item.expiry_ts = max(item.expiry_ts, expiry_ts)
        else:
            # Cache miss, unseen or forgotten key.
            self.misses += 1

            item = S3FIFOItem(key, expiry_ts, item_size)
            self.table[key] = item

            # Insert into small fifo.
            self.ensure_free(curr_timestamp)
            self.insertS(item)

    def insertM(self, item):
        item.freq = 0
        self.M.appendleft(item)
        self.m_size += item.size

    def insertS(self, item):
        self.S.appendleft(item)
        self.s_size += item.size

    def insertG(self, new_item, curr_timestamp):
        assert new_item.expiry_ts <= curr_timestamp
        # Evict items from G if it will be full. Items that have not been adopted into another queue are completely removed from the cache.
        while self.g_size + new_item.size >= self.target_len_m:
            tail_item = self.G.pop()
            self.g_size -= tail_item.size
            if tail_item.freq < 0:
                del self.table[tail_item.key]

        new_item.freq = -1
        self.G.appendleft(new_item)
        self.g_size += new_item.size

    def ensure_free(self, curr_timestamp):
        'Ensure there is at least one location free for a new item'
        while self.s_size + self.m_size >= self.size:
            if self.m_size >= self.target_len_m or self.s_size == 0:
                self.evictM(curr_timestamp)
            else:
                # We need the outer while loop because if every item in S is eligible for promotion to M, then evictS() will not evict anything to G and we will need to call evictM().
                self.evictS(curr_timestamp)

    def evictM(self, curr_timestamp):
        # Evict something, completely removing it from the cache. This may not evict an item if all items in the queue will expire in the future. In that case, we'll raise an exception. In a real use case, the system probably shouldn't have received a request to cache this many elements because its cache is already full.
        frozen_items_visited = 0
        while self.m_size > 0 and frozen_items_visited < len(self.M):
            tail_item = self.M.pop()
            if tail_item.freq > 0 or tail_item.expiry_ts > curr_timestamp:
                # Reinsert.
                if tail_item.expiry_ts > curr_timestamp and tail_item.freq <= 1:
                    # If item needs to be frozen because it can't be expired, we'll increase our counter to get out of a potential infinite loop, because we can't decrease the frequency.
                    frozen_items_visited += 1
                else:
                    tail_item.freq -= 1
                    # We reset the count because we just got an item that's unfrozen, so it's possible we may be able to still evict something.
                    frozen_items_visited = 0
                self.M.appendleft(tail_item)
            else:
                # Evict. Item may still be in G.
                self.m_size -= tail_item.size
                del self.table[tail_item.key]
                return
        if frozen_items_visited >= len(self.M):
            raise Exception("We needed to evict something from M, but we can't evict anything because we're full!")

        assert False, 'Unreachable!'

    def evictS(self, curr_timestamp):
        # Promote items into M until we find an item we can demote to G or run out of items. Note that we'll only move items to G if both its frequency is <= 0 AND the item is already expired. There are cases when frequency is <= 0 (and on normal S3FIFO would be moved to G), but the item is not yet expired.
        while self.s_size > 0:
            # Find a tail item that is either unexpired and we can naturally move to M, or is expired and we can move to G. If neither is true, we'll forcibly move items to M later in the code.
            item_promoted = False
            for i in range(1 - len(self.S), -1, -1):
                tail_item = self.S[i]
                if tail_item.freq > 0:
                    # Item can be promoted to M. We don't care if it's expired or not, because it got enough hits to be promoted.
                    self.S.remove(tail_item)
                    self.s_size -= tail_item.size
                    self.insertM(tail_item)
                    item_promoted = True
                    # We'll exit the loop and redo the steps because we still haven't moved anything to G.
                    break
                elif tail_item.freq <= 0 and tail_item.expiry_ts <= curr_timestamp:
                    # Item can be moved to G and is already expired, so we'll go ahead and move it.
                    self.S.remove(tail_item)
                    self.s_size -= tail_item.size
                    self.insertG(tail_item, curr_timestamp)
                    return

            if not item_promoted:
                # If we're here, means that self.s_size > 0 and we didn't find any item to send to G or to naturally promote to M. We'll forcibly move all items to M to keep with the original idea that if no item can be moved to G, we'll just end up promoting everything.
                while len(self.S) > 0:
                    tail_item = self.S.pop()
                    self.s_size -= tail_item.size
                    self.insertM(tail_item)
