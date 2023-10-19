import heapq
from dataclasses import dataclass, field

@dataclass(order=True)
class Invocation:
    end_ts: float
    size: float
    removed: bool = field(compare=False)
    identifier: str = field(compare=False)

# Min size for datasets/AzureFunctionsInvocationTraceProcessedDuplicated.txt: 7900.0
# Min size for datasets/AzureFunctionsDataset2019Processed_300M_001.txt: 252818.0
# Min size for datasets/AzureFunctionsDataset2019Processed_600M_001.txt: 252818.0
# Min size for datasets/AzureFunctionsDataset2019Processed_10G_001.txt: 304246.0
# Min size for datasets/AzureFunctionsDataset2019Processed.txt: 485924.0
def init_states(size=int(7900 * 1.1 + 1)):
    from size_time_aware_algs import FIFOTimed, S3FIFONaiveTimed
    from size_aware_algs import FIFOSized, S3FIFONaiveSized

    return {
        'time_algs': {
            'fifo': FIFOTimed(size=size),
            's3fifonaive': S3FIFONaiveTimed(size=size, max_pct_cached=0.1),
        },
        'size_algs': {
            'fifosized': FIFOSized(size=size),
            's3fifosized': S3FIFONaiveSized(size=size, max_pct_cached=0.1),
        },
        'sorted_invocations': [],
        'invocations_index': {},
        'existing_hits': 0,
        'total_cache_size': size,
        'running_invocations_size': 0,
    }

def get_item(state, start_ts, item_id, end_ts, item_size):
    for queue in state['time_algs'].values():
        queue.get(item_id, start_ts, end_ts, item_size)

def get_item_end(state, start_ts, item_id, end_ts, item_size):
    # Must remove all finished invocations from the heap before doing anything.
    sorted_invs = state['sorted_invocations']
    while len(sorted_invs) > 0 and (sorted_invs[0].removed or sorted_invs[0].end_ts <= start_ts):
        expired_item = heapq.heappop(sorted_invs)
        if expired_item.removed:
            # This was just a tombstone, nothing else to do with this item.
            continue

        del state['invocations_index'][expired_item.identifier]
        state['running_invocations_size'] -= expired_item.size

        new_queue_size = state['total_cache_size'] - state['running_invocations_size']
        for queue in state['size_algs'].values():
            queue.change_size(new_queue_size)

        for queue in state['size_algs'].values():
            # We're only populating the queue here, so we don't want to muddle the stats.
            queue.get(expired_item.identifier, expired_item.size, ignore_stats=True)

    if item_id in state['invocations_index']:
        state['existing_hits'] += 1
        existing_item = state['invocations_index'][item_id]
        new_end_ts = max(existing_item.end_ts, end_ts)

        if new_end_ts > existing_item.end_ts:
            # Mark the existing entry in the heap as removed (it'll be removed later), then add a new one.
            existing_item.removed = True

            state['invocations_index'][item_id] = Invocation(new_end_ts, existing_item.size, False, item_id)
            heapq.heappush(state['sorted_invocations'], state['invocations_index'][item_id])
    else:
        # We'll add the item to the list of running invocations, and also hit the caches to simulate retrieving this element from the cache. Whether it's a hit or miss will be recorded in the cache.
        new_item = Invocation(end_ts, item_size, False, item_id)
        state['invocations_index'][item_id] = new_item
        heapq.heappush(state['sorted_invocations'], new_item)
        state['running_invocations_size'] += item_size
        assert state['running_invocations_size'] <= state['total_cache_size']

        for queue in state['size_algs'].values():
            # This is done so we can record stats when hitting the cache. We'll remove the item right away because it's going on the list of running invocations.
            queue.get(item_id, item_size)
            queue.remove_item(item_id)

        new_queue_size = state['total_cache_size'] - state['running_invocations_size']
        for queue in state['size_algs'].values():
            queue.change_size(new_queue_size)

def run_tests_for_csv(filename):
    import csv

    state = init_states()

    total_operations = 0
    with open(filename, 'r') as f:
        reader = csv.reader(f)

        for start_ts, end_ts, item_id, item_size in reader:
            total_operations += 1
            get_item(state, float(start_ts), item_id, float(end_ts), float(item_size))
            get_item_end(state, float(start_ts), item_id, float(end_ts), float(item_size))
    
    print('Time and size-aware algorithms:')
    for queue in state["time_algs"].values():
        print(f'  {type(queue).__name__}: hit rate {queue.hits / total_operations} (hits={queue.hits}, misses={queue.misses})')
    print('Size-aware algorithms (item added when invocation is done):')
    for queue in state["size_algs"].values():
        print(f"  {type(queue).__name__}: hit rate {(queue.hits + state['existing_hits']) / total_operations} (existing_hits={state['existing_hits']}, hits={queue.hits}, misses={queue.misses})")


if __name__ == '__main__':
    import sys

    run_tests_for_csv(sys.argv[1])
