from abc import ABCMeta, abstractmethod
import numpy as np

class SimilarityModel:

    __metaclass__ = ABCMeta

	@abstractmethod
    def getSimilarityMapBetweenParagraphsOfDocuments(self, ps1, ps2):
        pass

	@abstractmethod
    def getSimilarityMapBetweenSentencesOfSentences(self, p1, p2):
        pass
		
class TFIDFModel(SimilarityModel):

	def __init__(self, stoplistfile=None):
		self.stoplist = set([line.strip() for line in open(stoplistfile)])
		
	def getSimilarityMapBetweenParagraphsOfDocuments(self, ps1=[], ps2=[]):
		#Get TFIDF model controllers:
		tfidf, index, sent_indexes, sent_similarities = self.getTFIDFControllers(ps1, ps2)
	
		#Calculate paragraph similarities:
		paragraph_similarities = list(np.zeros((len(ps1), len(ps2))))
		for i, p1 in enumerate(ps1):
			for j, p2 in enumerate(ps2):
				values = []
				for sent1 in p1:
					for sent2 in p2:
						values.append(sent_similarities[sent_indexes[cps]][sent_indexes[sps]])
				paragraph_similarities[i][j] = np.max(values)
				
		#Return similarity matrix:
		return paragraph_similarities
				
	def getTFIDFController(self, ps1, ps2):
		#Get paragraph sizes:
		sizep1 = len(p1)
		sizep2 = len(p2)
		
		#Get paragraph sentence maps:
		p1map = getSentenceMap(p1)
		p2map = getSentenceMap(p2)
		
		#Create data structure for TFIDF model:
		documents = []
		sents1 = set(p1map.keys())
		sents2 = set(p2map.keys())
		allsents = list(sents1.union(sents2))
		sent_indexes = {}
		for i, s in enumerate(allsents):
			documents.append(s.strip())
			sent_indexes[s] = i
			
		#Get TFIDF model and similarity querying framework:
		texts = [[word for word in document.split() if word not in self.stoplist] for document in documents]
		dictionary = gensim.corpora.Dictionary(texts)
		corpus = [dictionary.doc2bow(text) for text in texts]
		tfidf = gensim.models.TfidfModel(corpus)
		index = gensim.similarities.MatrixSimilarity(tfidf[corpus])
		
		#Create TFIDF similarity matrix:
		sent_similarities = []
		for j in range(0, len(allsents)):
			sims = index[tfidf[corpus[j]]]
			sent_similarities.append(sims)
				
		#Return controllers:
		return tfidf, index, sent_indexes, sent_similarities
