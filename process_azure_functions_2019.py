import csv
import hashlib
import numpy as np
import metalog

def process():
    app_functions = {}
    app_functions_per_day = []
    app_sizes = {}
    function_to_app = {}

    function_params_per_day = []

    for i in range(1, 15):
        filename = f'datasets/azurefunctions-dataset2019/function_durations_percentiles.anon.d{i:02}.csv'

        day_functions = {}
        day_function_params = {}

        with open(filename, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row['HashFunction'] not in function_to_app:
                    function_to_app[row['HashFunction']] = row['HashApp']

                if row['HashApp'] not in app_functions:
                    app_functions[row['HashApp']] = set()
                
                if row['HashApp'] not in day_functions:
                    day_functions[row['HashApp']] = set()
                
                app_functions[row['HashApp']].add(row['HashFunction'])
                day_functions[row['HashApp']].add(row['HashFunction'])

                row_p0 = float(row['percentile_Average_0'])
                row_p100 = float(row['percentile_Average_100'])
                percentiles = [float(row['percentile_Average_1']), float(row['percentile_Average_25']), float(row['percentile_Average_50']), float(row['percentile_Average_75']), float(row['percentile_Average_99'])]

                all_vals = [row_p0]
                all_vals.extend(percentiles)
                all_vals.append(row_p100)

                for j in range(6):
                    if all_vals[j + 1] - all_vals[j] < 0:
                        print(f"Something's wrong with this row! all_vals={all_vals}")
                        raise Exception('ugh')

                if row['HashFunction'] in day_function_params:
                    print(f"Hash function params already in day {i} for func {row['HashFunction']}!")
                    continue
                
                day_function_params[row['HashFunction']] = (row_p0, row_p100, percentiles)
        
        app_functions_per_day.append(day_functions)
        function_params_per_day.append(day_function_params)

        if i >= 13:
            continue

        filename = f'datasets/azurefunctions-dataset2019/app_memory_percentiles.anon.d{i:02}.csv'
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                max_mem_size = float(row['AverageAllocatedMb_pct100'])

                if row['HashApp'] in app_sizes:
                    app_sizes[row['HashApp']] = max(app_sizes[row['HashApp']], max_mem_size)
                else:
                    app_sizes[row['HashApp']] = max_mem_size
        
    print(f'Total apps: {len(app_functions)}')

    total_functions = sum([len(value) for value in app_functions.values()])
    print(f'Total functions: {total_functions}')

    for i in range(14):
        day = i + 1
        print(f'Total apps for day {day}: {len(app_functions_per_day[i])}')

        def exists_in_other_days(app_id):
            for j in range(14):
                if j == i:
                    continue
                if app_id in app_functions_per_day[j]:
                    return True
            return False

        total_functions_this_day = sum([len(value) for value in app_functions_per_day[i].values()])
        print(f'Total functions on day {day}: {total_functions_this_day}')

        apps_only_this_day = [app for app in app_functions_per_day[i] if not exists_in_other_days(app)]
        print(f'Apps only for day {day}: {len(apps_only_this_day)}')

    rng = np.random.default_rng()

    processed_file = open('datasets/AzureFunctionsDataset2019Processed.txt', 'w')
    
    for i in range(14):
        day = i + 1
        filename = f'datasets/azurefunctions-dataset2019/invocations_per_function_md.anon.d{day:02}.csv'

        function_params = function_params_per_day[i]
        invocations_for_the_day = []
        day_timestamp_begin = i * 1440 * 60

        per_minute_invocation_nums = [{} for _ in range(1440)]
        per_minute_invocations = [[] for _ in range(1440)]

        funcs_on_this_day = set()

        print(f'Reading day {day}')

        with open(filename, 'r') as f:
            reader = csv.DictReader(f)

            total_funcs_not_in_day = 0

            for row in reader:
                if row['HashFunction'] not in function_params:
                    total_funcs_not_in_day += 1
                    continue

                funcs_on_this_day.add(row['HashFunction'])

                for j in range(1440):
                    invocations_to_simulate = int(row[str(j + 1)])
                    if invocations_to_simulate > 0:
                        if row['HashFunction'] not in per_minute_invocation_nums[j]:
                            per_minute_invocation_nums[j][row['HashFunction']] = invocations_to_simulate
                        else:
                            per_minute_invocation_nums[j][row['HashFunction']] += invocations_to_simulate

        print(f"Found {total_funcs_not_in_day} total functions not in the percentiles for this day, but they have invocation numbers. Weird.")

        total_invocations = sum([sum(minute_data.values()) for minute_data in per_minute_invocation_nums])
        print(f'There are {total_invocations} invocations for this day.')

        chunk_start = 0
        for chunk_end in range(0, 1440, 40):
            print(f'Procesing funcs for day {day}, start = {chunk_start} end = {chunk_end}')

            for func_id in funcs_on_this_day:
                if function_to_app[func_id] not in app_sizes:
                    continue

                p0, p100, percentiles = function_params[func_id]
                percentile_nums = [0.01, 0.25, 0.5, 0.75, 0.99]

                use_single_value = p0 == p100

                if not use_single_value:
                    first_non_diff = 0
                    for k in range(6):
                        first_non_diff = k
                        if k == 5:
                            break
                        if p0 != percentiles[k]:
                            break

                    non_diff_value = 0
                    if first_non_diff == 5:
                        if p100 == percentiles[4]:
                            use_single_value = True
                        else:
                            non_diff_value = p100
                    else:
                        non_diff_value = percentiles[first_non_diff]

                    if not use_single_value:
                        for k in range(first_non_diff):
                            percentiles[k] += 0.01 * (non_diff_value - p0)
                
                if not use_single_value:
                    first_non_diff = 4
                    for k in range(4, -2, -1):
                        first_non_diff = k
                        if k == -1:
                            break
                        if p100 != percentiles[k]:
                            break

                    non_diff_value = 0
                    if first_non_diff == -1:
                        if p0 == percentiles[0]:
                            use_single_value = True
                        else:
                            non_diff_value = p0
                    else:
                        non_diff_value = percentiles[first_non_diff]

                    if not use_single_value:
                        for k in range(4, first_non_diff, -1):
                            percentiles[k] -= 0.01 * (p100 - non_diff_value)

                if not use_single_value:
                    z = metalog.logit_z(percentiles, p0, p100)
                    sample_func = metalog.metalog_logit_func(4, percentiles, percentile_nums, z)
                else:
                    sample_func = lambda _: p0

                for j in range(chunk_start, chunk_end):
                    if func_id not in per_minute_invocation_nums[j]:
                        continue

                    timestamp_begin = day_timestamp_begin + j * 60
                    invocations_to_simulate = per_minute_invocation_nums[j][func_id]

                    if invocations_to_simulate > 0:
                        invocation_timestamps = rng.random(invocations_to_simulate)
                        invocation_keys = rng.random(invocations_to_simulate)

                        for k in range(invocations_to_simulate):
                            duration = sample_func(invocation_keys[k])
                            start = timestamp_begin + invocation_timestamps[k] * 60
                            end = start + duration
                            per_minute_invocations[j].append((start, end, function_to_app[func_id]))

            for j in range(chunk_start, chunk_end):
                print(f'Processing day {day} minute {j + 1}')
                print(f'There are {len(per_minute_invocations[j])} invocations in this minute.')

                per_minute_invocations[j].sort()
                for start, end, app in per_minute_invocations[j]:
                    if app not in app_sizes:
                        continue
                    processed_file.write(f'{start},{end},{app},{app_sizes[app]}\n')

                processed_file.flush()
                per_minute_invocations[j] = []

            chunk_start = chunk_end

    close(processed_file)

if __name__ == '__main__':
    process()