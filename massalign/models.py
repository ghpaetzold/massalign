from abc import ABCMeta, abstractmethod
import numpy as np
import gensim
import codecs

class SimilarityModel:

	__metaclass__ = ABCMeta

	@abstractmethod
	def getSimilarityMapBetweenParagraphsOfDocuments(self, ps1, ps2):
		pass

	@abstractmethod
	def getSimilarityMapBetweenSentencesOfParagraphs(self, p1, p2):
		pass
		
class TFIDFModel(SimilarityModel):

	def __init__(self, input_files=[], stoplistfile=None):
		self.stoplist = set([line.strip() for line in codecs.open(stoplistfile, encoding='utf8')])
		self.tfidf, self.dictionary = self.getTFIDFmodel(input_files)
		
	def getTFIDFmodel(self, input_files=[]):
		#Create text sentence set for training:
		sentences = []
		for file in input_files:
			f = codecs.open(file, encoding='utf8')
			for line in f:
				sentence = [word for word in line.strip().split(' ') if word not in self.stoplist]
				sentences.append(sentence)
			f.close()
				
		#Train TFIDF model:
		dictionary = gensim.corpora.Dictionary(sentences)
		corpus = [dictionary.doc2bow(sentence) for sentence in sentences]
		tfidf = gensim.models.TfidfModel(corpus)
		
		#Return tfidf model:
		return tfidf, dictionary
	
	def getSimilarityMapBetweenSentencesOfParagraphs(self, p1, p2):
		#Get distinct sentences from paragraphs:
		sentences = list(self.getSentencesFromParagraph(p1).union(self.getSentencesFromParagraph(p2)))
		
		#Get TFIDF model controllers:
		sentence_indexes, sentence_similarities = self.getTFIDFControllers(sentences)
		
		#Return similarity matrix:
		return sentence_similarities, sentence_indexes
		
	def getSimilarityMapBetweenParagraphsOfDocuments(self, ps1=[], ps2=[]):
		#Get distinct sentences from paragraph sets:
		sentences = list(self.getSentencesFromParagraphs(ps1).union(self.getSentencesFromParagraphs(ps2)))

		#Get TFIDF model controllers:
		sentence_indexes, sentence_similarities = self.getTFIDFControllers(sentences)
	
		#Calculate paragraph similarities:
		paragraph_similarities = list(np.zeros((len(ps1), len(ps2))))
		for i, p1 in enumerate(ps1):
			for j, p2 in enumerate(ps2):
				values = []
				for sent1 in p1:
					for sent2 in p2:
						values.append(sentence_similarities[sentence_indexes[sent1]][sentence_indexes[sent2]])
				paragraph_similarities[i][j] = np.max(values)
				
		#Return similarity matrix:
		return paragraph_similarities, sentence_indexes
				
	def getTFIDFControllers(self, sentences):		
		#Create data structures for similarity calculation:
		sent_indexes = {}
		for i, s in enumerate(sentences):
			sentences.append(s.strip())
			sent_indexes[s] = i
			
		#Get similarity querying framework:
		texts = [[word for word in sentence.split(' ') if word not in self.stoplist] for sentence in sentences]
		corpus = [self.dictionary.doc2bow(text) for text in texts]
		index = gensim.similarities.MatrixSimilarity(self.tfidf[corpus])
		
		#Create similarity matrix:
		sentence_similarities = []
		for j in range(0, len(allsents)):
			sims = index[self.tfidf[corpus[j]]]
			sentence_similarities.append(sims)
				
		#Return controllers:
		return sent_indexes, sentence_similarities
		
	def getSentencesFromParagraphs(self, ps):
		#Get all distinct sentences from a set of paragraphs:
		sentences = set([])
		for p in ps:
			psents = self.getSentencesFromParagraph(p)
			sentences.update(psents)
		
		#Return sentences found:
		return sentences
	
	def getSentencesFromParagraph(self, p):
		#Return all distinct sentences from a paragraph:
		return set(p)
			
		
