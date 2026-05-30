from multiprocessing import Pool
import os
import gc

from utils import timer_func, printd

def _process_chunk(args:tuple[int,int,str]) -> dict[bytes,list[int|float]]:
    start, end, filename = args
    local: dict[bytes,list[int|float]] = {}
    with open(filename, 'rb') as f:
        f.seek(start)
        gc.disable()
        for line in f.read((end - start)).split(b'\n'):
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
        gc.enable()
    return local

def generate_marching_orders(target_filename:str, cpu_count:int) -> list[tuple[int,int,str]]:
    file_size = os.path.getsize(target_filename)
    step = max(2**22, file_size // (cpu_count * 2))
    n_steps = file_size // step
    
    print(f'USING {n_steps} CHUNKS and {cpu_count} CPUs')
    chunks: list[tuple[int,int,str]] = []
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
    
    return chunks


def march(chunks:list[tuple[int,int,str]], cpu_count:int):
    d: dict[bytes, list[float | int]] = dict() # min, max, sum, count

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
    return d


@timer_func
def run() -> None:
    cpu_count = os.cpu_count() or 1
    chunks = generate_marching_orders(target_filename='data/measurements.csv', cpu_count=cpu_count)
    res = march(chunks=chunks, cpu_count=cpu_count)
    printd(res)



if __name__ == '__main__':
    run()
