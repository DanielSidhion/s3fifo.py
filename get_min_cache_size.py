from dataclasses import dataclass, field
import heapq

@dataclass(order=True)
class Invocation:
    end_ts: float
    size: float
    removed: bool = field(compare=False)
    identifier: str = field(compare=False)

def get_min_cache_size(filename):
    import csv
    import matplotlib.pyplot as plt

    total_invocations = 0

    max_running_size = 0
    curr_running_size = 0
    invs = {}
    sorted_invs = []

    # times = []
    # running_sizes = []

    with open(filename, 'r') as f:
        reader = csv.reader(f)

        for start_ts, end_ts, item_id, item_size in reader:
            total_invocations += 1

            if total_invocations % 10000000 == 0:
                print(f'Total invocations already processed: {total_invocations}')

            start_ts = float(start_ts)
            end_ts = float(end_ts)
            item_size = float(item_size)

            # Expire all invocations that finished already.
            while len(sorted_invs) > 0 and (sorted_invs[0].removed or sorted_invs[0].end_ts <= start_ts):
                expired_item = heapq.heappop(sorted_invs)

                if not expired_item.removed:
                    curr_running_size -= expired_item.size
                    assert curr_running_size >= 0
                    del invs[expired_item.identifier]

            if item_id in invs:
                existing_end_ts = invs[item_id].end_ts
                new_end_ts = max(invs[item_id].end_ts, end_ts)

                if new_end_ts > existing_end_ts:
                    # Mark the existing entry in the heap as removed (it'll be removed later), then add a new one.
                    invs[item_id].removed = True

                    invs[item_id] = Invocation(new_end_ts, invs[item_id].size, False, item_id)
                    heapq.heappush(sorted_invs, invs[item_id])
            else:
                invs[item_id] = Invocation(end_ts, item_size, False, item_id)
                heapq.heappush(sorted_invs, invs[item_id])
                curr_running_size += item_size
            
            max_running_size = max(max_running_size, curr_running_size)
            # times.append(start_ts)
            # running_sizes.append(curr_running_size)

    print(f'Min cache size for all invocations to work: {max_running_size}')
    # fig, ax = plt.subplots()
    # ax.plot(times, running_sizes)
    # plt.axhline(y=max_running_size, color='r', linestyle='-')
    # plt.show()

if __name__ == '__main__':
    import sys

    get_min_cache_size(sys.argv[1])
