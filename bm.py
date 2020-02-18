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

	def pickVictim(self, buffer):
		for i in range(2 * (len(buffer))):
			if buffer[self.location].pinCount == 0 and buffer[self.location].referenced == 0:
				return self.location  # We are selecting self.location as our victim
			else:
				buffer[self.location].referenced = 0
				self.location += 1
				if self.location == len(buffer):
					self.location = 0
		raise BufferPoolFullError("Buffer Pool Full")


# ==================================================================================================
		
class bufferManager:
	
	def __init__(self, size):
		self.buffer = []
		self.clk = clock()
		self.dm = diskManager()
		for i in range(size):
			self.buffer.append(frame()) # creating buffer frames (i.e., allocating memory)
			self.buffer[i].frameNumber = i

	# ------------------------------------------------------------

	def pin(self, pageNumber, new=False):
		# given a page number, pin the page in the buffer
		# if new = True, the page is new so no need to read it from disk
		# if new = False, the page already exists. So read it from disk if it is not already in the pool.
		myFrame = self.clk.pickVictim(self.buffer)  # returns an int
		# print (type(myFrame))
		# print ("frame picked",victim) ##for debugging
		if self.buffer[myFrame].currentPage.pageNo == pageNumber:
			self.buffer[myFrame].pinCount += 1
			self.buffer[myFrame].referenced = 1
			return self.buffer[myFrame].currentPage
		if self.buffer[myFrame].dirtyBit == True:
			self.dm.writePageToDisk(self.buffer[myFrame].currentPage)
		# if page is not new, read page pageNo from disk into frame
		if new == False:
			self.buffer[myFrame].currentPage.pageNo = self.dm.readPageFromDisk(pageNumber).pageNo
			self.buffer[myFrame].currentPage.content = self.dm.readPageFromDisk(pageNumber).content
		else:
			# page is new
			self.buffer[myFrame].currentPage.pageNo = pageNumber
		self.buffer[myFrame].pinCount += 1
		self.buffer[myFrame].referenced = 1
		self.buffer[myFrame].dirtyBit = False
		return self.buffer[myFrame].currentPage

	# ------------------------------------------------------------

	def unpin(self, pageNumber, dirty):
		'''
		self.printBufferContent()
		for frame in self.buffer:
			if frame.pinCount > 0 and not frame.referenced == 1:
				frame.pinCount = frame.pinCount - 1
				if dirty:
					self.dm.writePageToDisk(frame.currentPage)
			elif frame.pinCount == 0 and not frame.referenced == 1:
				if dirty:
					self.dm.writePageToDisk(frame.currentPage)
					dirty = False
		'''			# loop through buffer pool, find page which matches pageNumber, decrement pin, if dirty, dirty = True
		self.printBufferContent()
		for frame in self.buffer:
			if frame.currentPage.pageNo == pageNumber:
				if frame.pinCount > 0:
					frame.pinCount = frame.pinCount -1
					if dirty:
						frame.dirtyBit = True
	# ------------------------------------------------------------

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
