import random

COLDEST_TEMP = -99.9
HOTTEST_TEMP =  99.9

def main():
    locations = get_locations()
    write_new_measurements(locations)


def get_locations():
    locations = []

    with open('weather_stations.csv', 'r', encoding='utf-8') as f:
        f.readline()
        f.readline()
        while True:
            try:
                loc, _ = f.__next__().strip('\n').split(';',1)
                locations.append(loc)
            except StopIteration:
                break
        
    return locations

def write_new_measurements(locations, n = 1_000_000_000, batch_size=10_000):

    n_batches = n//batch_size
    with open('measurements.csv', 'wb') as f:

        for bidx in range(n_batches):
            if bidx%10 == 0:
                print(f"Batch {bidx} / {n_batches}")
            b = random.choices(locations, k=batch_size)
            z = [bytes(f"{station};{random.uniform(COLDEST_TEMP, HOTTEST_TEMP):.1f}\n", encoding='utf-8') for station in b]
            # prepped_deviated_batch = '\n'.join(z) # :.1f should quicker than round on a large scale, because round utilizes mathematical operation
            f.writelines(z)
            # f.write(prepped_deviated_batch)
        

    

if __name__ == '__main__':
    main()