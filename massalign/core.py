import os, gensim
import numpy as np
import codecs
from aligners import *
from models import *

class MASSAligner:
	
	def __init__(self):
		pass
		
	def getParagraphsFromDocument(self, document_path):
		#Open file and initialize variables:
		f = codecs.open(document_path, encoding='utf8')
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
		#Employ the paragraph aligner provided to align paragraphs from documents:
		return paragraph_aligner.alignParagraphsFromDocuments(paragraphs1, paragraphs2)
		
	def getSentenceAlignments(self, paragraph1=[], paragraph2=[], sentence_aligner=None):
		#Employ the sentence aligner provided to align sentences from paragraphs:
		return sentence_aligner.alignSentencesFromParagraphs(paragraph1, paragraph2)