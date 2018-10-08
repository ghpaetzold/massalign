import codecs

try:
    # for Python2
    from urllib2 import urlopen
except ImportError:
    # for Python3
    from urllib.request import urlopen


class FileReader:
	"""
	A convenience class that allows you to more easily read local and online files.
	
	* *Parameters*:
		* **path**: A path to a local file or a url to an online file.
		* **stop_list**: A set of stop words.
	"""
	
	def __init__(self, path, stop_list=set([])):
		self.path = path
		self.stop_list = stop_list
	
	def getRawText(self):
		"""
		Reads the input file and outputs the raw text in it.
		
		* *Output*:
			* **text**: Raw text within the file.
		"""
		text = ''
		if self.path.startswith('http'):
			text = urlopen(self.path).read().decode('utf8').strip()
		else:
			f = codecs.open(self.path, encoding='utf8')
			text = f.read().strip()
			f.close()
		return text
	
	def getSplitSentences(self):
		"""
		Reads the input file and produces a list of split sentences.
		
		* *Output*:
			* **sentences**: List of sentences. Each sentence is a list of words.
		"""
		sentences = []
		if self.path.startswith('http'):
			text = str(urlopen(self.path).read())
			for line in text.strip().split('\n'):
				sentence = [word for word in line.strip().split(' ') if word not in self.stop_list]
				sentences.append(sentence)
		else:
			f = codecs.open(self.path, encoding='utf8')
			for line in f:
				sentence = [word for word in line.strip().split(' ') if word not in self.stop_list]
				sentences.append(sentence)
			f.close()
		return sentences
		
	