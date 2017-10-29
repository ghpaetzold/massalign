import os, gensim
import numpy as np
from annotators import *
from aligners import *
from models import *
from gui import *

class MASSAligner:
	"""
	A convenience class that allows you to more easily join aligners and annotators.
	"""
	
	def __init__(self):
		pass
		
	def getParagraphsFromDocument(self, document_path):
		"""
		Extracts a list of paragraphs from a document.
		
		* *Parameters*:
			* **document_path**: A path to a document of which each line represents a sentence and paragraphs are separated by an empty line.
		* *Output*:
			* **paragraphs**: An instance of a class deriving from SimilarityModel.
		"""
		#Open file and initialize variables:
		reader = FileReader(document_path)
		text = reader.getRawText().split('\n')
		paragraphs = []
		
		#Begin search for paragraphs:
		newparag = []
		curr_line = 0
		line = text[curr_line].strip()
		while curr_line<len(text) and len(line)>0:
			#Search for full paragraph:
			newparag.append(line)
			curr_line += 1
			line = text[curr_line].strip()
			while curr_line<len(text) and len(line)>0:
				newparag.append(line)
				curr_line += 1
				if curr_line<len(text):
					line = text[curr_line].strip()
			
			#Save newly found paragraph:
			paragraphs.append(newparag)

			#Continue search for next paragraph
			newparag = []
			curr_line += 1
			if curr_line<len(text):
				line = text[curr_line].strip()
		
		#Return found paragraphs:
		return paragraphs
		
	def getParagraphAlignments(self, paragraphs1=[], paragraphs2=[], paragraph_aligner=None, **kwargs):
		"""
		Extracts paragraph alignments from two lists of paragraphs from comparable documents.
		
		* *Parameters*:
			* **paragraphs1**: A list of source paragraphs. A paragraph is a list of sentences.
			* **paragraphs2**: A list of target paragraphs. A paragraph is a list of sentences.
			* **paragraph_aligner**: An instance of a class deriving from ParagraphAligner.
			* **kwargs**: Any complementary parameters taken as input by the paragraph aligner.
		* *Output*:
			* The output is the same produced by the paragraph aligner upon calling the "alignParagraphsFromDocuments" function.
		"""
		#Employ the paragraph aligner provided to align paragraphs from documents:
		if len(paragraphs1)>0 and len(paragraphs2)>0:
			return paragraph_aligner.alignParagraphsFromDocuments(paragraphs1, paragraphs2, **kwargs)
		else:
			return [], []
		
	def getSentenceAlignments(self, paragraph1=[], paragraph2=[], sentence_aligner=None, **kwargs):
		"""
		Extracts paragraph alignments from two lists of paragraphs from comparable documents.
		
		* *Parameters*:
			* **paragraph1**: A source paragraph. A paragraph is a list of sentences.
			* **paragraph2**: A target paragraph. A paragraph is a list of sentences.
			* **sentence_aligner**: An instance of a class deriving from SentenceAligner.
			* **kwargs**: Any complementary parameters taken as input by the sentence aligner.
		* *Output*:
			* The output is the same produced by the sentence aligner upon calling the "alignSentencesFromParagraphs" function.
		"""
		#Employ the sentence aligner provided to align sentences from paragraphs:
		if len(paragraph1)>0 and len(paragraph2)>0:
			return sentence_aligner.alignSentencesFromParagraphs(paragraph1, paragraph2, **kwargs)
		else:
			return [], []
		
	def getSentenceAnnotations(self, sentence1='', sentence2='', sentence_annotator=None, **kwargs):
		"""
		Produces word-level annotations from two parallel sentences.
		
		* *Parameters*:
			* **sentence1**: A source sentence.
			* **sentence2**: A target sentence.
			* **sentence_annotator**: An instance of a class deriving from SentenceAnnotator.
			* **kwargs**: Any complementary parameters taken as input by the sentence annotator.
		* *Output*:
			* The output is the same produced by the sentence annotator upon calling the "annotate_sentence" function.
		"""
		#Employ the sentence annotator provided to annotate a pair of aligned sentences:
		if len(sentence1)>0 and len(sentence2)>0:
			return sentence_annotator.annotate_sentence(sentence1, sentence2, **kwargs)
		else:
			return {}
			
	def visualizeParagraphAlignments(self, paragraphs1=[], paragraphs2=[], alignments=[]):
		"""
		Displays alignments between lists of paragraphs.
		
		* *Parameters*:
			* **paragraphs1**: A list of source paragraphs. A paragraph is a list of sentences.
			* **paragraphs2**: A list of target paragraphs. A paragraph is a list of sentences.
			* **alignments**: An alignment path between the input paragraph lists.
		* *Output*:
			* Opens an interface showcasing aligned paragraphs.
		"""
		gui = BasicGUI()
		gui.displayParagraphAlignments(paragraphs1, paragraphs2, alignments)
		
	def visualizeListOfParagraphAlignments(self, list_of_paragraph_sets1=[], list_of_paragraph_sets2=[], list_of_alignment_paths=[], **kwargs):
		"""
		Displays alignments between lists of lists of paragraphs.
		Each list of paragraphs can represent a document, so this function allows you to see the paragraph alignments of an entire collection of documents through a single interface.
		
		* *Parameters*:
			* **list_of_paragraph_sets1**: A source list of paragraph lists. A paragraph is a list of sentences.
			* **list_of_paragraph_sets2**: A source list of paragraph lists. A paragraph is a list of sentences.
			* **list_of_alignment_paths**: List of alignment paths between each pair of paragraph lists.
		* *Output*:
			* Opens an interface showcasing the aligned paragraphs for each pair of paragraph lists.
		"""
		gui = BasicGUI(**kwargs)
		gui.displayListOfParagraphAlignments(list_of_paragraph_sets1, list_of_paragraph_sets2, list_of_alignment_paths, **kwargs)
			
	def visualizeSentenceAlignments(self, paragraph1=[], paragraph2=[], alignments=[], **kwargs):
		"""
		Displays sentence alignments between two paragraphs.
		
		* *Parameters*:
			* **paragraph1**: A source paragraph. A paragraph is a list of sentences.
			* **paragraph2**: A target paragraph. A paragraph is a list of sentences.
			* **alignments**: An alignment path between the input paragraphs.
		* *Output*:
			* Opens an interface showcasing sentence alignments for a paragraph pair.
		"""
		gui = BasicGUI(**kwargs)
		gui.displaySentenceAlignments(paragraph1, paragraph2, alignments, **kwargs)
			
	def visualizeListOfSentenceAlignments(self, list_of_paragraphs1=[], list_of_paragraphs2=[], list_of_alignment_paths=[], **kwargs):
		"""
		Displays alignments between the sentences of each pair of paragraphs in a pair of paragraph lists.
		The interface will showcase the sentence-level alignments between each paragraph pair through a single interface.
		
		* *Parameters*:
			* **list_of_paragraphs1**: A source list of paragraphs. A paragraph is a list of sentences.
			* **list_of_paragraphs2**: A source list of paragraphs. A paragraph is a list of sentences.
			* **list_of_alignment_paths**: List of alignment paths between each pair of paragraphs.
		* *Output*:
			* Opens an interface showcasing the aligned sentences for each pair of paragraphs.
		"""
		gui = BasicGUI(**kwargs)
		gui.displayListOfSentenceAlignments(list_of_paragraphs1, list_of_paragraphs2, list_of_alignment_paths, **kwargs)
		
	def visualizeSentenceAnnotations(self, sentence1='', sentence2='', word_alignments='', annotations=[], **kwargs):
		"""
		Displays word-level annotations for a pair of aligned sentences.
		
		* *Parameters*:
			* **sentence1**: A source sentence.
			* **sentence2**: A target sentence.
			* **word_alignments**: Word alignments in Pharaoh format.
			* **annotations**: Word-level annotations produced for the sentence pair.
		* *Output*:
			* Opens an interface showcasing the word-level annotations for the aligned sentences.
		"""
		gui = BasicGUI(**kwargs)
		gui.displaySentenceAnnotations(sentence1, sentence2, word_alignments, annotations, **kwargs)
