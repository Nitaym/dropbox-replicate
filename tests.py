from multiprocessing.pool import ThreadPool
import time


def test(i):
    print("Start")
    time.sleep(3)
    print("Done")
    return i

if __name__ == "__main__":
    d = (1, 2, 3)

    values = range(5)
    results = ThreadPool(5).imap_unordered(test, values)
    for result in results:
        print(result)
