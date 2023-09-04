from dataclasses import dataclass

@dataclass
class Invocation:
    end_ts: float
    size: float

def get_min_cache_size(filename):
    import csv
    import matplotlib.pyplot as plt

    max_running_size = 0
    curr_running_size = 0
    invs = {}

    times = []
    running_sizes = []

    with open(filename, 'r') as f:
        reader = csv.reader(f)

        for start_ts, end_ts, item_id, item_size in reader:
            start_ts = float(start_ts)
            end_ts = float(end_ts)
            item_size = float(item_size)

            if item_id in invs:
                invs[item_id].end_ts = max(invs[item_id].end_ts, end_ts)
            else:
                invs[item_id] = Invocation(end_ts, item_size)
                curr_running_size += item_size

            # Expire all invocations that finished already.
            keys_to_expire = []
            for k in invs:
                if invs[k].end_ts <= start_ts:
                    curr_running_size -= invs[k].size
                    keys_to_expire.append(k)
            for k in keys_to_expire:
                del invs[k]
            
            max_running_size = max(max_running_size, curr_running_size)
            times.append(start_ts)
            running_sizes.append(curr_running_size)

    print(f'Min cache size for all invocations to work: {max_running_size}')
    fig, ax = plt.subplots()
    ax.plot(times, running_sizes)
    plt.axhline(y=max_running_size, color='r', linestyle='-')
    plt.show()

if __name__ == '__main__':
    import sys

    get_min_cache_size(sys.argv[1])
