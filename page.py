class page:
	# a page basically contains a pageNo and content.
	# the content typically contains a few records. However, we use a string for simplicitily
	def __init__(self,pageNo=None, content=None):
		if pageNo == None:
			self.pageNo = -1
		else:
			self.pageNo = pageNo

		if content == None:
			self.content = ""
		else:
			self.content = content 