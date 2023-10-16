import csv
import hashlib

def process():
    app_functions = {}
    invocations = []

    with open('datasets/AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt', 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row['app'] not in app_functions:
                app_functions[row['app']] = set()
            app_functions[row['app']].add(row['func'])
            end_timestamp = float(row['end_timestamp'])
            duration = float(row['duration'])
            start_timestamp = end_timestamp - duration
            invocations.append((start_timestamp, end_timestamp, row['app']))

    print(f'Total apps: {len(app_functions)}')

    total_functions = sum([len(value) for value in app_functions.values()])
    print(f'Total functions: {total_functions}')
    
    app_sizes = {key: len(value) * 100 for key, value in app_functions.items()}
    app_sizes_entries = list(map(lambda x: [x[1], x[0]], app_sizes.items()))
    app_sizes_entries.sort(reverse=True)

    print(f'Biggest app sizes: {app_sizes_entries[:20]}')

    invocations.sort()

    with open('datasets/AzureFunctionsInvocationTraceProcessed.txt', 'w') as f:
        for start, end, app in invocations:
            f.write(f'{start},{end},{app},{app_sizes[app]}\n')
        f.flush()

    with open('datasets/AzureFunctionsInvocationTraceProcessedDuplicated.txt', 'w') as f:
        last_ts = 0
        for start, end, app in invocations:
            f.write(f'{start},{end},{app},{app_sizes[app]}\n')
            last_ts = max(last_ts, end)
        
        last_ts += 10
        for start, end, app in invocations:
            new_app = hashlib.sha256(app.encode('utf-8')).hexdigest()
            f.write(f'{start + last_ts},{end + last_ts},{new_app},{app_sizes[app]}\n')

        f.flush()

if __name__ == '__main__':
    process()