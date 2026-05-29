from multiprocessing import Pool
# from multiprocessing
import sys
import time
import cProfile
# from typing import 

import pstats
from pstats import SortKey
import io
import os

import gc
d: dict[bytes, list] = dict() # min, max, sum, count

def _process_chunk(args):
    start, end, filename = args
    local = {}
    with open(filename, 'rb') as f:
        f.seek(start)
        gc.disable()
        for line in f.read(end - start).split(b'\n'):
            if not line:
                continue
            si = line.find(b';')
            loc = line[:si]
            temperature = float(line[si+1:])

            try:
                _local = local[loc]
                if temperature < _local[0]:
                    _local[0] = temperature
                if temperature > _local[1]:
                    _local[1] = temperature
                _local[2] += temperature
                _local[3] += 1
            except KeyError:
                local[loc] = [temperature, temperature, temperature, 1]


            # if loc in local:
            #     v = local[loc]
            #     if temperature < v[0]:
            #         v[0] = temperature
            #     if temperature > v[1]:
            #         v[1] = temperature
            #     v[2] += temperature
            #     v[3] += 1
            # else:
            #     local[loc] = [temperature, temperature, temperature, 1]
        gc.enable()
    return local




def main(cpu_count = os.cpu_count(), target_filename = 'measurements.csv', peek_dist = 25 ):

    file_size = os.path.getsize(target_filename)
    step = max(2**22, file_size // (cpu_count * 2))
    n_steps = file_size // step
    
    print(f'USING {n_steps} CHUNKS and {cpu_count} CPUs')
    chunks = []
    with open(target_filename, mode='r+b') as f:

        def is_new_line(pos:int):
            if pos == 0:
                return True
            f.seek(pos-1)
            return f.read(1) == b'\n'

        def next_line(pos:int):
            f.seek(pos)
            f.readline()
            return f.tell()

        chunk_start=0
        while chunk_start < file_size:
            chunk_end = min(file_size, chunk_start + step)

            while not is_new_line(chunk_end):
                chunk_end -= 1

            if chunk_start == chunk_end:
                chunk_end = next_line(chunk_end)

            chunks.append((chunk_start, chunk_end, target_filename))
            chunk_start = chunk_end

    with Pool(cpu_count) as pool:
        for partial in pool.imap_unordered(_process_chunk, chunks):
            for loc, v in partial.items():
                if loc in d:
                    _d = d[loc]
                    if v[0] < _d[0]:
                        _d[0] = v[0]
                    if v[1] > _d[1]:
                        _d[1] = v[1]
                    _d[2] += v[2]
                    _d[3] += v[3]
                else:
                    d[loc] = v

    printd()

def printd():
    print("{",end="")

    while len(d) >= 2:
        (k, vs) = d.popitem()
        k = k.decode('utf-8')
        print(f'{k}={vs[0]:.1f}/{vs[2]/vs[3]:.1f}/{vs[1]:.1f}, ',end='')
    k, vs = d.popitem()
    k = k.decode('utf-8')
    print(f'{k}={vs[0]:.1f}/{vs[2]/vs[3]:.1f}/{vs[1]:.1f}',end='')
    print("}")




# 249.645 seconds on 5 CPUs
# 50.493 seconds on 32 CPUs (128 chunks)
# 53.776 seconds on 64 CPUs (128 chunks)
if __name__ == "__main__":

    # ob = cProfile.Profile()

    # define_chunks()

    # ob.enable()
    # ob.disable()
    # sec = io.StringIO()

    # sortby = SortKey.TIME
    # ps = pstats.Stats(ob, stream=sec).sort_stats(sortby)
    # ps.print_stats()

    # print(sec.getvalue())

    start = time.time_ns()
    main()
    end = time.time_ns()

    print(f'Execution took {(end-start)/1e9:.2f} seconds')

