import cProfile
import random
from multiprocessing import Pool

COLDEST_TEMP = -99.9
HOTTEST_TEMP =  99.9

def get_locations() -> list[bytes]:
    locations:list[bytes] = []

    with open('weather_stations.csv', 'r+b') as f:
        for line in f.readlines(): #b'\n'
            si = line.find(b';')
            locations.append(line[:si].decode(encoding='utf-8',errors='ignore'))
    return locations

def generate_and_write_sample_data(args) -> None:
    locations, k = args[0], args[1]
    out_str = ''
    sampled_locations = random.choices(locations,k=k)

    for station in sampled_locations:
        out_str += f"{station};{random.uniform(COLDEST_TEMP, HOTTEST_TEMP):.1f}\n" #for station in sampled_locations

    with open('measurements.csv', 'a',encoding='utf-8') as f:
        f.write(out_str)

def main():
    locations = get_locations()
    # Write a million datapoints per function call. 
    N = 1_000_000_000
    k = 1_000_000

    import os
    pool = Pool(processes=os.cpu_count())
    pool.map(generate_and_write_sample_data, [(locations,k) for _ in range(N//k)])
    pool.close()
    pool.join()

if __name__ == '__main__':
    # cProfile.run('main()')

    main()