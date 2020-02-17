from page import page

class frame:
	def __init__(self):
		self.frameNumber = -1 # you may or may not use this attribute 
		self.pinCount =0
		self.dirtyBit = False
		self.referenced = 0
		self.currentPage = page()