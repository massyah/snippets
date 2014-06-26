#!/usr/bin/env python
# encoding: utf-8

"""
Demo implementation for easy independent threads support
"""

import collections,os
import logging
import threading
import itertools

from Queue import *
NMAXTHREADS=6


# Logger 


if "logger" not in globals():
	logger = logging.getLogger('test_logger')
	logger.setLevel(logging.DEBUG)

	# while len(logger.handlers()) > 0:
	#  	logger.pop()

	# create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	# create formatter
	formatter = logging.Formatter('%(asctime)s - %(filename)s - %(message)s',"%Y-%m-%d %H:%M:%S")
	# formatter = logging.Formatter('%(asctime)s - %(message)s')
	# add formatter to ch
	ch.setFormatter(formatter)

	# add ch to logger
	logger.addHandler(ch)


logger = logging.getLogger('test_logger')


# Multi threading support, generic 

class Worker(threading.Thread):
	def __init__(self, function, in_queue, out_queue):
		self.function = function
		self.in_queue, self.out_queue = in_queue, out_queue
		super(Worker, self).__init__()

	def run(self):
		while True:
			try:
				if self.in_queue.empty(): 
					break
				data = self.in_queue.get()
				result = self.function(data)
				self.out_queue.put((data,result))
				self.in_queue.task_done()
				logger.info("Still %d to do",self.in_queue.qsize())
			except Exception as e:
				logger.critical('something happened!: Error on %s, %s',repr(data),repr(e))
				self.out_queue.put({})
				self.in_queue.task_done()
				break

def process(data, function, num_workers=1):
	in_queue = Queue()
	for item in data:
		in_queue.put(item)
	out_queue = Queue(maxsize=in_queue.qsize())
	print in_queue,in_queue.unfinished_tasks
	workers = [Worker(function, in_queue, out_queue) for i in xrange(num_workers)]
	for worker in workers: 
		worker.setDaemon(True)
		worker.start()
	in_queue.join()
	return out_queue





## We define a processing function, feeding the process one: Adapt as needed 
def process_unit(input_list):
	a,b=input_list
	return str(a*b*2)



inputs_1=range(10)
inputs_2=range(10)
all_pairs=itertools.product(inputs_1,inputs_2)

# We launch on 10 threads
results=process(all_pairs,process_unit,10)

## get the content back

print results.queue