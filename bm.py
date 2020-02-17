from page import page
from frame import frame
from dm import diskManager

class BufferPoolFullError(Exception):
	#exception used in the Clock class
	def __init__(self, message):
		self.message = message
class clock:
	def __init__(self):
		# do the required initializations
		self.location = 0

	def pickVictim(self,buffer):
		try:
			for i in range(2*(len(buffer))):
				if buffer[self.location].pinCount == 0 and buffer[self.location].referenced == 0:
					return self.location		# We are selecting self.location as our victim
				else:
					buffer[self.location].referenced = 0
					self.location += 1
					if self.location == len(buffer):
						self.location = 0

		except BufferPoolFullError as error:
			print(error.message)

# ==================================================================================================
		
class bufferManager:
	
	def __init__(self,size):
		self.buffer = []
		self.clk = clock()
		self.dm = diskManager()
		for i in range(size):
			self.buffer.append(frame()) # creating buffer frames (i.e., allocating memory)
			self.buffer[i].frameNumber = i
	# ------------------------------------------------------------

	def pin(self, pageNumber, new = False):
		# given a page number, pin the page in the buffer
		# if new = True, the page is new so no need to read it from disk
		# if new = False, the page already exists. So read it from disk if it is not already in the pool. 
		my_frame = self.clk.pickVictim(self.buffer)  # returns an int
		# print(type(myFrame))
		# print("Frame picked", victim)  # For Debugging
		if self.buffer[my_frame].currentPage.pageNo == pageNumber:
			self.buffer[my_frame].pinCount += 1
			return self.buffer[my_frame]
		if self.buffer[my_frame].dirtyBit:
			self.dm.writePageToDisk(self.buffer[my_frame].currentPage)
		# if page is not new, read page pageNo from disk into frame
		if not new:
			self.buffer[my_frame].currentPage.pageNo = self.dm.readPageFromDisk(self.buffer[my_frame].currentPage.pageNo)
			self.buffer[my_frame].currentPage.content = self.dm.readPageFromDisk(self.buffer[my_frame].currentPage.content)
		else:
			# if page is new, then:
			self.buffer[my_frame].currentPage.pageNo = pageNumber
		self.buffer[my_frame].pinCount += 1
		self.buffer[my_frame].dirtyBit = False
		return self.buffer[my_frame]

	# ------------------------------------------------------------
	def unpin(self, pageNumber, dirty):
		print(type(pageNumber))
		self.printBufferContent()
		for frame in self.buffer:
			if frame.pinCount > 0 and not frame.referenced == 1:
				frame.pinCount = frame.pinCount - 1
				if frame.pinCount == 0 and dirty:
					self.dm.writePageToDisk(frame.currentPage)
			elif frame.pinCount == 0 and not frame.referenced == 1:
				if dirty:
					self.dm.writePageToDisk(frame.currentPage)
					dirty = False
			elif frame.referenced == 1:  # It should be logically impossible to reach this state
				print("Invalid operation - attempted to unpin a page which was referenced")


	def flushPage(self, pageNumber):
		# Ignore this function, it is not needed for this homework.
		# flushPage forces a page in the buffer pool to be written to disk
		for i in range(len(self.buffer)):
			if self.buffer[i].currentPage.pageNo == pageNumber:
				self.dm.writePageToDisk(self.buffer[i].currentPage) # flush writes a page to disk
				self.buffer[i].dirtyBit = False

	def printBufferContent(self):  # helper function to display buffer content on the screen (helpful for debugging)
		print("---------------------------------------------------")
		for i in range(len(self.buffer)):
			print("frame#={} pinCount={} dirtyBit={} referenced={} pageNo={} pageContent={} ".format(self.buffer[i].frameNumber, self.buffer[i].pinCount, self.buffer[i].dirtyBit, self.buffer[i].referenced,  self.buffer[i].currentPage.pageNo, self.buffer[i].currentPage.content))	
		print("---------------------------------------------------")
