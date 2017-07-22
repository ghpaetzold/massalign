from abc import ABCMeta, abstractmethod
import numpy as np

class ParagraphAligner:

    __metaclass__ = ABCMeta

    @abstractmethod
    def alignParagraphsFromDocuments(self):
        pass
		
class SentenceAligner:

    __metaclass__ = ABCMeta

    @abstractmethod
    def alignSentencesFromDocuments(self):
        pass
		
class VicinityDrivenParagraphAligner(ParagraphAligner):

	def __init__(self, similarity_model=None, acceptable_similarity=0.3):
		self.total_vicinity = set([(1,1),(1,0),(0,1),(2,1),(1,2)])
		self.first_vicinity = set([(1,1),(1,0),(0,1)])
		self.second_vicinity = set([(1,2),(2,1)])
		self.acceptable_similarity = acceptable_similarity
		self.similarity_model = similarity_model
		
	def alignParagraphsFromDocuments(self, p1s=[], p2s=[]):
		#Get similarity model:
		paragraph_similarities = self.similarity_model.getSimilarityMapBetweenParagraphsOfDocuments(p1s, p2s)
		
		#Calculate alignment path:
		alignment_path = self.getParagraphAlignmentPath(p1s, p2s, paragraph_similarities)
		
		#Produce actual alignments:
		aligned_paragraphs = self.getActualAlignedParagraphs(p1s, p2s, alignment_path)
		
		#Return alignment path:
		return alignment_path, aligned_paragraphs
		
	def getSentenceMap(self, paragraphs):
		#Allocate map:
		map = {}
		
		#Create a map from sentence to paragraph indexes:
		for i, p in enumerate(paragraphs):
			for sentence in p:
				if sentence not in map:
					map[sentence] = set([])
				map[sentence].add(i)
		
		#Return map:
		return map
		
	def getParagraphAlignmentPath(self, p1s, p2s, paragraph_similarities):
		#Get paragraph sizes:
		sizep1 = len(p1s)
		sizep2 = len(p2s)
		
		#Start vicinity-driven path search:
		path = [(0, 0)]
		currXY = (0, 0)
		
		#While matrix edges are not found, do:
		while currXY[0]<sizep1-1 or currXY[1]<sizep2-1:
			nextXY, nextXYsim = self.getNextAlignment(currXY, paragraph_similarities)
			if nextXY[0]==sizep1-1 and nextXY[1]==sizep2-1:
				if nextXYsim>=0.3:
					path.append(nextXY)
			else:
				path.append(nextXY)
			currXY = nextXY

		#Structure path found:
		for j, node in enumerate(path):
			path[j] = [[node[0]],[node[1]]]

		#Compact the path with 1-1, 1-N and N-1 alignments:
		compact_path = []
		while len(path)>0:
			top = path[0]
			if len(path)==1:
				compact_path.append(top)
				path.pop(0)
			else:
				next = path[1]
				if top[0]==next[0]:
					for al in next[1]:
						top[1].append(al)
					path.pop(1)
				elif top[1]==next[1]:
					for al in next[0]:
						top[0].append(al)
					path.pop(1)
				else:
					compact_path.append(top)
					path.pop(0)
		
		#Return resulting path:
		return compact_path
		
	def getNextAlignment(self, currXY, paragraph_similarities):
		#Get the similarities from all reachable candidates:
		cands = {}
		for pos in self.total_vicinity:
			candXY = (currXY[0]+pos[0], currXY[1]+pos[1])
			sim = -99999
			try:
				sim = paragraph_similarities[candXY[0]][candXY[1]]
			except Exception:
				pass
			cands[candXY] = sim
		
		#Rank them according to their similarities:
		winners = sorted(cands.keys(), key=cands.__getitem__, reverse=True)

		#Check whether the first ficinity has a similar enough candidate:
		nearest = [cands[(currXY[0]+pos[0], currXY[1]+pos[1])] for pos in self.first_vicinity]
		if np.max(nearest)>=self.acceptable_similarity:
			auxes = [(currXY[0]+pos[0], currXY[1]+pos[1]) for pos in self.second_vicinity]
			for aux in auxes:
					winners.remove(aux)
			return winners[0], cands[winners[0]]
		#If not, check the second vicinity:
		else:
			all = [cands[c] for c in cands]
			#If not, get a next synchronizer outside the reachable vicinity
			if np.max(all)<self.acceptable_similarity:
				finalNextXY = self.getNextSynchronizer(currXY, paragraph_similarities)
				return finalNextXY, paragraph_similarities[finalNextXY[0]][finalNextXY[1]]
			else:
				return winners[0], cands[winners[0]]

	def getNextSynchronizer(self, currXY, paragraph_similarities):
		#Start search for next synchronizer:
		cands = {}
		orig = currXY
		last = [len(paragraph_similarities), len(paragraph_similarities[0])]
		
		#Find all candidates "in front" of currXY that have good enough similarity:
		for i in range(orig[0], last[0]):
			for j in range(orig[1], last[1]):
				if i!=orig[0] and j!=orig[1] and paragraph_similarities[i][j]>=self.acceptable_similarity:
					cands[(i, j)] = (i-orig[0])+(j-orig[1])
					
		#If there are any, get the best one:
		if len(cands)>0:
			closest = sorted(cands.keys(), key=cands.__getitem__)
			return closest[0]
		#Otherwise, return the last position in the alignment matrix:
		else:
			return (last[0]-1, last[1]-1)
			
	def getActualAlignedParagraphs(self, p1s, p2s, alignment_path):
		#Create structure to store aligned paragraphs:
		aligned_paragraphs = []
		
		#For each alignment in the path, produce final aligned text of both sides:
		for node in alignment_path:
			c = self.getOriginalParagraph(node[0], p1s)
			s = self.getOriginalParagraph(node[1], p2s)
			aligned_paragraphs.append([c, s])
		
		#Return aligned paragraphs:
		return aligned_paragraphs:
				
	def getOriginalParagraph(self, aligned_nodes, paragraphs):
		#Concatenate all sentences from all paragraphs in an aligned node:
		text = ''
		for index in aligned_nodes:
			for sentence in paragraphs[index]:
				text += sentence + '\n'
		return text.strip()

####################################################################################################################################################
			
class VicinityDrivenSentenceAligner(SentenceAligner):

	def __init__(self, similarity_model=None, acceptable_similarity=0.3):
		self.total_vicinity = set([(1,1),(1,0),(0,1),(2,1),(1,2)])
		self.first_vicinity = set([(1,1),(1,0),(0,1)])
		self.second_vicinity = set([(1,2),(2,1)])
		self.acceptable_similarity = acceptable_similarity
		self.similarity_model = similarity_model
		
	def alignParagraphsFromDocuments(self, p1s=[], p2s=[]):
		#Get similarity model:
		paragraph_similarities = self.similarity_model.getSimilarityMapBetweenParagraphsOfDocuments(p1s, p2s)
		
		#Calculate alignment path:
		path = self.getParagraphAlignmentPath(p1s, p2s, paragraph_similarities)
		
		#Return alignment path:
		return path
		
	def getSentenceMap(self, paragraphs):
		#Allocate map:
		map = {}
		
		#Create a map from sentence to paragraph indexes:
		for i, p in enumerate(paragraphs):
			for sentence in p:
				if sentence not in map:
					map[sentence] = set([])
				map[sentence].add(i)
		
		#Return map:
		return map
		
	def getParagraphAlignmentPath(self, p1s, p2s, paragraph_similarities):
		#Get paragraph sizes:
		sizep1 = len(p1s)
		sizep2 = len(p2s)
		
		#Start vicinity-driven path search:
		path = [(0, 0)]
		currXY = (0, 0)
		
		#While matrix edges are not found, do:
		while currXY[0]<sizep1-1 or currXY[1]<sizep2-1:
			nextXY, nextXYsim = self.getNextAlignment(currXY, paragraph_similarities)
			if nextXY[0]==sizep1-1 and nextXY[1]==sizep2-1:
				if nextXYsim>=0.3:
					path.append(nextXY)
			else:
				path.append(nextXY)
			currXY = nextXY

		#Structure path found:
		for j, node in enumerate(path):
			path[j] = [[node[0]],[node[1]]]

		#Compact the path with 1-1, 1-N and N-1 alignments:
		compact_path = []
		while len(path)>0:
			top = path[0]
			if len(path)==1:
				compact_path.append(top)
				path.pop(0)
			else:
				next = path[1]
				if top[0]==next[0]:
					for al in next[1]:
						top[1].append(al)
					path.pop(1)
				elif top[1]==next[1]:
					for al in next[0]:
						top[0].append(al)
					path.pop(1)
				else:
					compact_path.append(top)
					path.pop(0)
		
		#Return resulting path:
		return compact_path
		
	def getNextAlignment(self, currXY, paragraph_similarities):
		#Get the similarities from all reachable candidates:
		cands = {}
		for pos in self.total_vicinity:
			candXY = (currXY[0]+pos[0], currXY[1]+pos[1])
			sim = -99999
			try:
				sim = paragraph_similarities[candXY[0]][candXY[1]]
			except Exception:
				pass
			cands[candXY] = sim
		
		#Rank them according to their similarities:
		winners = sorted(cands.keys(), key=cands.__getitem__, reverse=True)

		#Check whether the first ficinity has a similar enough candidate:
		nearest = [cands[(currXY[0]+pos[0], currXY[1]+pos[1])] for pos in self.first_vicinity]
		if np.max(nearest)>=self.acceptable_similarity:
			auxes = [(currXY[0]+pos[0], currXY[1]+pos[1]) for pos in self.second_vicinity]
			for aux in auxes:
					winners.remove(aux)
			return winners[0], cands[winners[0]]
		#If not, check the second vicinity:
		else:
			all = [cands[c] for c in cands]
			#If not, get a next synchronizer outside the reachable vicinity
			if np.max(all)<self.acceptable_similarity:
				finalNextXY = self.getNextSynchronizer(currXY, paragraph_similarities)
				return finalNextXY, paragraph_similarities[finalNextXY[0]][finalNextXY[1]]
			else:
				return winners[0], cands[winners[0]]

	def getNextSynchronizer(self, currXY, paragraph_similarities):
		#Start search for next synchronizer:
		cands = {}
		orig = currXY
		last = [len(paragraph_similarities), len(paragraph_similarities[0])]
		
		#Find all candidates "in front" of currXY that have good enough similarity:
		for i in range(orig[0], last[0]):
			for j in range(orig[1], last[1]):
				if i!=orig[0] and j!=orig[1] and paragraph_similarities[i][j]>=self.acceptable_similarity:
					cands[(i, j)] = (i-orig[0])+(j-orig[1])
					
		#If there are any, get the best one:
		if len(cands)>0:
			closest = sorted(cands.keys(), key=cands.__getitem__)
			return closest[0]
		#Otherwise, return the last position in the alignment matrix:
		else:
			return (last[0]-1, last[1]-1)
