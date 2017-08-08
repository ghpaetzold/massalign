import os, gensim
import numpy as np
import codecs
from annotators import *
from aligners import *
from models import *
from gui import *

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
		
	def getParagraphAlignments(self, paragraphs1=[], paragraphs2=[], paragraph_aligner=None, **kwargs):
		#Employ the paragraph aligner provided to align paragraphs from documents:
		if len(paragraphs1)>0 and len(paragraphs2)>0:
			return paragraph_aligner.alignParagraphsFromDocuments(paragraphs1, paragraphs2, **kwargs)
		else:
			return [], []
		
	def getSentenceAlignments(self, paragraph1=[], paragraph2=[], sentence_aligner=None, **kwargs):
		#Employ the sentence aligner provided to align sentences from paragraphs:
		if len(paragraph1)>0 and len(paragraph2)>0:
			return sentence_aligner.alignSentencesFromParagraphs(paragraph1, paragraph2, **kwargs)
		else:
			return [], []
		
	def getSentenceAnnotations(self, sentence1=[], sentence2=[], sentence_annotator=None, **kwargs):
		#Employ the sentence annotator provided to annotate a pair of aligned sentences:
		if len(sentence1)>0 and len(sentence2)>0:
			return sentence_annotator.annotate_sentence(sentence1, sentence2, **kwargs)
		else:
			return {}
			
	def visualizeParagraphAlignments(self, paragraph_set1=[], paragraph_set2=[], alignments=[], **kwargs):
		gui = BasicGUI(**kwargs)
		gui.displayParagraphAlignments(paragraph_set1, paragraph_set2, alignments, **kwargs)
		
	def visualizeListOfParagraphAlignments(self, list_of_paragraph_sets1=[], list_of_paragraph_sets2=[], list_of_alignments=[], **kwargs):
		gui = BasicGUI(**kwargs)
		gui.displayListOfParagraphAlignments(list_of_paragraph_sets1, list_of_paragraph_sets2, list_of_alignments, **kwargs)
			
	def visualizeSentenceAlignments(self, paragraph1=[], paragraph2=[], alignments=[], **kwargs):
		gui = BasicGUI(**kwargs)
		gui.displaySentenceAlignments(paragraph1, paragraph2, alignments, **kwargs)
			
	def visualizeListOfSentenceAlignments(self, list_of_paragraphs1=[], list_of_paragraphs2=[], alignments=[], **kwargs):
		gui = BasicGUI(**kwargs)
		gui.displayListOfSentenceAlignments(list_of_paragraphs1, list_of_paragraphs2, alignments, **kwargs)
		
	def visualizeSentenceAnnotations(self, sentence1=[], sentence2=[], word_alignments=[], annotations=[], **kwargs):
		gui = BasicGUI(**kwargs)
		gui.displaySentenceAnnotations(sentence1, sentence2, word_alignments, annotations, **kwargs)
