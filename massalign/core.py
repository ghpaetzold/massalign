import os, gensim
import numpy as np
from nltk.util import ngrams
from aligners import *

class MASSAligner:
	
	def __init__(self):
		pass
		
	def getParagraphsFromDocument(self, document_path):
		#Open file and initialize variables:
		f = open(document_path)
		paragraphs = []
		
		#Begin search for paragraphs:
		newparag = []
		line = f.readline().strip()
		while len(line)>0:
			#Search for full paragraph:
			newparag.append(line)
			line = f.readline().strip()
			while len(line)>0:
				newparag.append(line)
				line = f.readline().strip()
			
			#Save newly found paragraph:
			paragraphs.append(newparag)

			#Continue search for next paragraph
			newparag = []
			line = f.readline().strip()
		f.close()
		
		#Return found paragraphs:
		return paragraphs
		
	def getParagraphAlignments(self, paragraphs1=[], paragraphs2=[], paragraph_aligner=None):
		return []