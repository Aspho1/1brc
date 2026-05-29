import sys
import time
import cProfile

def main():
    d = dict() # min, max, sum, count
    # z = 0
    with open("measurements.csv", 'r', encoding='utf-8') as f:

        for line in f:
            # z+=1
            
            loc, temp = line.rstrip().split(";", 1)
            loc = sys.intern(loc)
            temp = float(temp)
            if loc not in d:
                d[loc] = (99.9, -99.9, 0, 0)
            d[loc] = (min(d[loc][0], temp), max(d[loc][1], temp), d[loc][2]+temp, d[loc][3]+1)
            # if z %1000 == 0: 
            #     print(loc, d[loc])

    print("{",end="")

    while len(d) > 1:
        (k, vs) = d.popitem()
        print(f'{k}={vs[0]:.1f}/{vs[2]/vs[3]:.1f}/{vs[1]:.1f}, ',end='')
    k, vs = d.popitem()
    print(f'{k}={vs[0]:.1f}/{vs[2]/vs[3]:.1f}/{vs[1]:.1f}',end='')
    print("}",end="")


if __name__ == "__main__":

    cProfile.run("main()")
    # start = time.time_ns()
    # main()
    # end = time.time_ns()

    # print(f'Execution took {(end-start)/1e9} seconds')