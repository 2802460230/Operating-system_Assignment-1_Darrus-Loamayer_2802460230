import threading
import random

#run Measure-Command { python "Assignment 1.py" | Out-Host } for timing  

# I had to run cd "C:\Users\Darrus Loamayer\Desktop\Operating system"
#python "Assignment 1.py" for it to work  

# Constants
LOWER_NUM = 1
UPPER_NUM = 10000
BUFFER_SIZE = 100
MAX_COUNT = 10000

buffer = []
buffer_lock = threading.Lock()
not_full = threading.Condition(buffer_lock)
not_empty = threading.Condition(buffer_lock)

consumed_count = 0
consumed_lock = threading.Lock()

all_file = open("all.txt", "w")
even_file = open("even.txt", "w")
odd_file = open("odd.txt", "w")
file_lock = threading.Lock()

produced_count = 0
producer_done = False


def producer():
    global produced_count, producer_done

    for _ in range(MAX_COUNT):
        num = random.randint(LOWER_NUM, UPPER_NUM)

        with not_full:
            while len(buffer) >= BUFFER_SIZE:
                not_full.wait()
            buffer.append(num)
            not_empty.notify_all()

        with file_lock:
            all_file.write(f"{num}\n")

        with consumed_lock:
            produced_count += 1

    producer_done = True
    with not_empty:
        not_empty.notify_all()


def consumer_even():
    """Removes even numbers from top of stack, writes to odd.txt"""
    global consumed_count

    while True:
        with not_empty:
            while True:
                if buffer and buffer[-1] % 2 == 0:
                    num = buffer.pop()
                    not_full.notify_all()
                    break
                elif buffer and buffer[-1] % 2 != 0:
                    not_empty.wait(timeout=0.001)
                elif not buffer:
                    if producer_done:
                        with consumed_lock:
                            if consumed_count >= MAX_COUNT:
                                return
                    not_empty.wait(timeout=0.001)

        with file_lock:
            odd_file.write(f"{num}\n")  # even numbers go to odd.txt

        with consumed_lock:
            consumed_count += 1
            if consumed_count >= MAX_COUNT:
                return


def consumer_odd():
    """Removes odd numbers from top of stack, writes to even.txt"""
    global consumed_count

    while True:
        with not_empty:
            while True:
                if buffer and buffer[-1] % 2 != 0:
                    num = buffer.pop()
                    not_full.notify_all()
                    break
                elif buffer and buffer[-1] % 2 == 0:
                    not_empty.wait(timeout=0.001)
                elif not buffer:
                    if producer_done:
                        with consumed_lock:
                            if consumed_count >= MAX_COUNT:
                                return
                    not_empty.wait(timeout=0.001)

        with file_lock:
            even_file.write(f"{num}\n")  # odd numbers go to even.txt

        with consumed_lock:
            consumed_count += 1
            if consumed_count >= MAX_COUNT:
                return


if __name__ == "__main__":
    t_producer = threading.Thread(target=producer)
    t_even = threading.Thread(target=consumer_even)
    t_odd = threading.Thread(target=consumer_odd)

    t_producer.start()
    t_even.start()
    t_odd.start()

    t_producer.join()
    t_even.join()
    t_odd.join()

    all_file.close()
    even_file.close()
    odd_file.close()

    print("Done.")