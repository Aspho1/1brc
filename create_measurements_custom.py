import cProfile
import random
from multiprocessing import Pool
import os

COLDEST_TEMP = -99.9
HOTTEST_TEMP =  99.9

def get_locations() -> list[bytes]:
    locations:dict[bytes, float] = {}

    with open('weather_stations.csv', 'r+b') as f:
        for line in f.readlines(): #b'\n'
            si = line.find(b';')
            loc = line[:si].decode(encoding='utf-8',errors='ignore')
            val = float(line[si+1:])

            locations[loc] = val

    return locations

def generate_and_write_sample_data(args) -> int:
    locations, k = args[0], args[1]
    out_str = ''
    sampled_locations = random.choices(list(locations.keys()),k=k)

    # Assigning a random sd (0-10) to each chunk
    sd = random.random()*10
    for station in sampled_locations:

        # sampling a normal dist for the temperature measurement using the provided mean and a random sd. clipping. 
        x = min(max(random.normalvariate(mu=locations[station], sigma=sd), -99.9) ,99.9)
        out_str += f"{station};{x:.1f}\n" 

    with open('measurements.csv', 'a',encoding='utf-8') as f:
        f.write(out_str)
    return 0

def main():
    locations = get_locations()
    N = 1_000_000_000
    cpus = os.cpu_count()
    k = N // (cpus*2)

    with Pool(processes=cpus) as pool:
        for r in pool.imap_unordered(generate_and_write_sample_data, [(locations,k) for _ in range(N//k)]):
            if r > 0:
                print("ERROR")

if __name__ == '__main__':
    # cProfile.run('main()')
    main()