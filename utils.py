from time import time
def printd(d:dict[bytes, list[float | int]]):
    print("{",end="")

    while len(d) >= 2:
        (k, vs) = d.popitem()
        k = k.decode('utf-8')
        print(f'{k}={vs[0]:.1f}/{vs[2]/vs[3]:.1f}/{vs[1]:.1f}, ',end='')
    k, vs = d.popitem()
    k = k.decode('utf-8')
    print(f'{k}={vs[0]:.1f}/{vs[2]/vs[3]:.1f}/{vs[1]:.1f}',end='')
    print("}")


def timer_func(func):
    # This function shows the execution time of 
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func