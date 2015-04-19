import heapq
import threading

class MessageQueue:
    def __init__(self, init_seq_num):
        self._last_seq = init_seq_num
        self._seqs = set()
        self._heap = []
        self._cv = threading.Condition()
        self._cv2 = threading.Condition()

    def push(self, msg_obj, seq_num):
        self._cv.acquire()
        if seq_num not in self._seqs and seq_num > self._last_seq:
            self._seqs.add(seq_num)
            heapq.heappush(self._heap, (seq_num, msg_obj))
            if seq_num == self._last_seq + 1:
                self._cv.notify_all()
        self._cv.release()

    def pop(self):
        self._cv2.acquire()

        self._cv.acquire()
        # Block the method if the message is missing
        if len(self._heap) == 0 or self._heap[0][0] > self._last_seq + 1:
            self._cv.wait()
        try:
            result = heapq.heappop(self._heap)
        except Exception:
            return None
        self._last_seq = result[0]
        self._seqs.remove(result[0])
        self._cv.release()

        self._cv2.release()

        return result[1]

    def set_last_seq(self, last_seq):
        self._cv.acquire()
        self._last_seq = last_seq
        self._cv.notify_all()
        self._cv.release()

    def notify_all(self):
        self._cv.acquire()
        self._cv.notify_all()
        self._cv.release()


# Test

# import time
# import random

# def t1():
#     global mq
#     for i in range(2000):
#         print mq.pop()

# def t2(l):
#     global mq
#     print l
#     for i in l:
#         mq.push("msg", i)
#         print "push: %s" % i

# mq = MessageQueue(0)
# l1 = range(1,1001)
# l2 = range(1001,2001)
# random.shuffle(l1)
# random.shuffle(l2)
# threading.Thread(target=t1).start()
# for i in range(10):
#     threading.Thread(target=t2, args=(l1[100*i:100*(i+1)]+l2[100*i:100*(i+1)],)).start()


