from abc import ABCMeta, abstractmethod
import numpy as np
import gensim
from massalign.util import FileReader

class SimilarityModel:

	__metaclass__ = ABCMeta

	@abstractmethod
	def getSimilarityMapBetweenParagraphsOfDocuments(self, ps1, ps2):
		pass

	@abstractmethod
	def getSimilarityMapBetweenSentencesOfParagraphs(self, p1, p2):
		pass
		
class TFIDFModel(SimilarityModel):
	"""
	Implements a typical gensim TFIDF model for MASSAlign.
			
	* *Parameters*:
		* **input_files**: A set of file paths containing text from which to extract TFIDF weight values.
		* **stop_list_file**: A path to a file containing a list of stop-words.
	"""

	def __init__(self, input_files=[], stop_list_file=None):
		reader = FileReader(stop_list_file)
		self.stoplist = set([line.strip() for line in reader.getRawText().split('\n')])
		self.tfidf, self.dictionary = self.getTFIDFmodel(input_files)
		
	def getTFIDFmodel(self, input_files=[]):
		"""
		Trains a gensim TFIDF model.
				
		* *Parameters*:
			* **input_files**: A set of file paths containing text from which to extract TFIDF weight values.
		* *Output*:
			* **tfidf**: A trained gensim models.TfidfModel instance.
			* **dictionary**: A trained gensim.corpora.Dictionary instance.
		"""
		#Create text sentence set for training:
		sentences = []
		for file in input_files:
			reader = FileReader(file, self.stoplist)
			sentences.extend(reader.getSplitSentences())
				
		#Train TFIDF model:
		dictionary = gensim.corpora.Dictionary(sentences)
		corpus = [dictionary.doc2bow(sentence) for sentence in sentences]
		tfidf = gensim.models.TfidfModel(corpus)
		
		#Return tfidf model:
		return tfidf, dictionary
	
	def getSimilarityMapBetweenSentencesOfParagraphs(self, p1, p2):
		"""
		Produces a matrix containing similarity scores between all sentences in a pair of paragraphs.
				
		* *Parameters*:
			* **p1**: A source paragraph. A paragraph is a list of sentences.
			* **p2**: A target paragraph. A paragraph is a list of sentences.
		* *Output*:
			* **sentence_similarities**: A matrix containing a similarity score between all possible pairs of sentences in the union of p1 and p2. The matrix's height and width are equal and equivalent to the number of distinct sentences present in the union of p1 and p2.
			* **sentence_indexes**: A map connecting each sentence to its numerical index in the sentence_similarities matrix.
		"""
		#Get distinct sentences from paragraphs:
		sentences = list(self.getSentencesFromParagraph(p1).union(self.getSentencesFromParagraph(p2)))
		
		#Get TFIDF model controllers:
		sentence_similarities, sentence_indexes = self.getTFIDFControllers(sentences)
		
		#Return similarity matrix:
		return sentence_similarities, sentence_indexes
		
	def getSimilarityMapBetweenParagraphsOfDocuments(self, p1s=[], p2s=[]):
		"""
		Produces a matrix containing similarity scores between all paragraphs in a pair of paragraph lists.
				
		* *Parameters*:
			* **p1s**: A list of source paragraphs. Each paragraph is a list of sentences.
			* **p2s**: A list of target paragraphs. Each paragraph is a list of sentences.
		* *Output*:
			* **paragraph_similarities**: A matrix containing a similarity score between all possible pairs of paragraphs in the union of p1 and p2. The matrix's height and width are equal and equivalent to the number of distinct paragraphs present in the union of p1s and p2s.
		"""
		#Get distinct sentences from paragraph sets:
		sentences = list(self.getSentencesFromParagraphs(p1s).union(self.getSentencesFromParagraphs(p2s)))

		#Get TFIDF model controllers:
		sentence_similarities, sentence_indexes = self.getTFIDFControllers(sentences)
	
		#Calculate paragraph similarities:
		paragraph_similarities = list(np.zeros((len(p1s), len(p2s))))
		for i, p1 in enumerate(p1s):
			for j, p2 in enumerate(p2s):
				values = []
				for sent1 in p1:
					for sent2 in p2:
						values.append(sentence_similarities[sentence_indexes[sent1]][sentence_indexes[sent2]])
				paragraph_similarities[i][j] = np.max(values)
				
		#Return similarity matrix:
		return paragraph_similarities
				
	def getTFIDFControllers(self, sentences):
		"""
		Produces TFIDF similarity scores between all possible pairs of sentences in a list.
				
		* *Parameters*:
			* **sentences**: A list of sentences.
		* *Output*:
			* **sentence_similarities**: A matrix containing a similarity score between all possible sentence pairs in the input sentence list. The matrix's height and width are equal and equivalent to the number of distinct sentences in the input sentence list.
			* **sentence_indexes**: A map connecting each sentence to its numerical index in the sentence_similarities matrix.
		"""
		#Create data structures for similarity calculation:
		sent_indexes = {}
		for i, s in enumerate(sentences):
			sent_indexes[s] = i
			
		#Get similarity querying framework:
		texts = [[word for word in sentence.split(' ') if word not in self.stoplist] for sentence in sentences]
		corpus = [self.dictionary.doc2bow(text) for text in texts]
		index = gensim.similarities.MatrixSimilarity(self.tfidf[corpus])
		
		#Create similarity matrix:
		sentence_similarities = []
		for j in range(0, len(sentences)):
			sims = index[self.tfidf[corpus[j]]]
			sentence_similarities.append(sims)
		
		#Return controllers:
		return sentence_similarities, sent_indexes
	
	def getTextSimilarity(self, buffer1, buffer2):
		"""
		Calculates the TFIDF similarity between two buffers containing text.
				
		* *Parameters*:
			* **buffer1**: A source buffer containing a block of text.
			* **buffer2**: A target buffer containing a block of text.
		* *Output*:
			* **similarity**: The TFIDF similarity between the two buffers of text.
		"""
		#Get bag-of-words vectors:
		vec1 = self.dictionary.doc2bow(buffer1.split())
		vec2 = self.dictionary.doc2bow(buffer2.split())
		corpus = [vec1, vec2]
		
		#Get similarity matrix from bag-of-words model:
		index = gensim.similarities.MatrixSimilarity(self.tfidf[corpus])
		
		#Return the similarity between the vectors:
		sims = index[self.tfidf[vec1]]
		similarity = sims[1]
		return similarity
	
	def getSentencesFromParagraphs(self, ps):
		"""
		Extracts a set containing all unique sentences in a list of paragraphs.
				
		* *Parameters*:
			* **ps**: A list of paragraphs. A paragraph is a list of sentences.
		* *Output*:
			* **sentences**: The set containing all unique sentences in the input paragraph list.
		"""
		#Get all distinct sentences from a set of paragraphs:
		sentences = set([])
		for p in ps:
			psents = self.getSentencesFromParagraph(p)
			sentences.update(psents)
		
		#Return sentences found:
		return sentences
	
	def getSentencesFromParagraph(self, p):
		"""
		Extracts a set containing all unique sentences in a paragraph.
				
		* *Parameters*:
			* **p**: A paragraph. A paragraph is a list of sentences.
		* *Output*:
			* **sentences**: The set containing all unique sentences in the input paragraph.
		"""
		#Return all distinct sentences from a paragraph:
		sentences = set(p)
		return sentences
			
		
