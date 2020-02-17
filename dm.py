import os
import glob
import pickle
from page import page

class diskManager:
		
	def writePageToDisk(self,page):	
		# very simple way to store a page on disk using the pickle library
		# note that a table/index pages are typically stored together in one file. 
		# However, for simplicity we store each page in a separate file.
		
		pickle.dump( page, open( "{}{}{}".format("pageFile", page.pageNo, ".pge"), "wb" ) )
		
	def readPageFromDisk(self,pageNo):
		with open("{}{}{}".format("pageFile", pageNo, ".pge"), 'rb') as pickle_file:
			page = pickle.load(pickle_file)
		return page
	
	def deleteAllPagesOnDisk(self):
		# A function to delete all page files from disk (clean up before a test is started)
		fileList = glob.glob('*.pge') # get all pages from disk (each page is stored in a .pge file)
		for file in fileList:
			try:
				os.remove(file)
			except:
				print("Error while deleting file : ", file)
				return False
		return True	

