from multiprocessing import Pool
# from multiprocessing
import sys
import threading
import time
import cProfile
# from typing import 

import pstats
from pstats import SortKey
import io
import os


d: dict[bytes, list] = dict() # min, max, sum, count

def _process_chunk(args):
    start, end, filename = args
    local = {}
    with open(filename, 'rb') as f:
        f.seek(start)
        for line in f.read(end - start).split(b'\n'):
            si = line.find(b';')
            loc, temp = line[:si], float(line[si+1:])
            if loc in local:
                v = local[loc]
                if temp < v[0]: v[0] = temp
                if temp > v[1]: v[1] = temp
                v[2] += temp
                v[3] += 1
            else:
                local[loc] = [temp, temp, temp, 1]
    return local


def main(cpu_count = os.cpu_count(), target_filename = 'measurements.csv', peek_dist = 25):

    file_size = os.path.getsize(target_filename)
    step = file_size // cpu_count

    chunks = []
    x=0
    with open(target_filename, 'r+b') as f:
        for i in range(cpu_count):
            start = x
            end = min(x+step,file_size)

            if end < file_size:
                f.seek(end)
                end += f.peek(peek_dist).find(b'\n') + 1
            chunks.append((start,end,target_filename))
            x=end

    with Pool(cpu_count) as pool:
        results = pool.map(_process_chunk, chunks)


    for partial in results:
        for loc, v in partial.items():
            if loc in d:
                d[loc][0] = min(d[loc][0], v[0])
                d[loc][1] = max(d[loc][1], v[1])
                d[loc][2] += v[2]
                d[loc][3] += v[3]
            else:
                d[loc] = v
    return d



        #     semicolon_idx = line.find(b";")
        #     loc, temp = line[:semicolon_idx], float(line[semicolon_idx+1:-1])
        #     if loc not in d:
        #         d[loc] = [temp, temp, temp, 1]
        #     else:
        #         if temp < d[loc][0]:
        #             d[loc][0] = temp
        #         if temp > d[loc][1]:
        #             d[loc][1] = temp
        #         d[loc][2] += temp
        #         d[loc][3] += 1

        #     z+=1
            # if z % 10000 == 0: 
            #     # print(loc, d[loc])
            #     if z > 1000000:
            #         return


def printd():

    print("{",end="")

    while len(d) > 1:
        (k, vs) = d.popitem()
        k = k.decode('utf-8')
        print(f'{k}={vs[0]:.1f}/{vs[2]/vs[3]:.1f}/{vs[1]:.1f}, ',end='')
    k, vs = d.popitem()
    k = k.decode('utf-8')
    print(f'{k}={vs[0]:.1f}/{vs[2]/vs[3]:.1f}/{vs[1]:.1f}',end='')
    print("}",end="")





if __name__ == "__main__":

    ob = cProfile.Profile()

    # define_chunks()

    ob.enable()
    d = main()
    ob.disable()
    printd(d)

    sec = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(ob, stream=sec).sort_stats(sortby)
    ps.print_stats()

    print(sec.getvalue())

    # start = time.time_ns()
    # main()
    # end = time.time_ns()

    # print(f'Execution took {(end-start)/1e9} seconds')