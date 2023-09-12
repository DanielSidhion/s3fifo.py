# Min size for datasets/AzureFunctionsDataset2019Processed_300M_001.txt: 252818
# Min size for datasets/AzureFunctionsDataset2019Processed_600M_001.txt: 252818
def init_states(size=252818):
    from size_time_aware_algs import FIFOTimed, S3FIFONaiveTimed

    return {
        "fifo": FIFOTimed(size=size * 1.1),
        "s3fifonaive": S3FIFONaiveTimed(size=int(size * 1.1), max_pct_cached=0.1)
    }

def get_item(state, start_ts, item_id, end_ts, item_size):
    for queue in state.values():
        queue.get(item_id, start_ts, end_ts, item_size)

def run_tests_for_csv(filename):
    import csv

    state = init_states()

    total_operations = 0
    with open(filename, 'r') as f:
        reader = csv.reader(f)

        for start_ts, end_ts, item_id, item_size in reader:
            total_operations += 1
            get_item(state, float(start_ts), item_id, float(end_ts), float(item_size))
    
    for queue in state.values():
        print(f'{type(queue).__name__}: hit rate {queue.hits / total_operations} (hits={queue.hits}, misses={queue.misses})')


if __name__ == '__main__':
    import sys

    run_tests_for_csv(sys.argv[1])
