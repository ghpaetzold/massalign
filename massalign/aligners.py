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
    def alignSentencesFromParagraphs(self):
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
		paragraph_similarities, sentence_indexes = self.similarity_model.getSimilarityMapBetweenParagraphsOfDocuments(p1s, p2s)
		
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
		#Get paragraph set sizes:
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
		return aligned_paragraphs
				
	def getOriginalParagraph(self, aligned_nodes, paragraphs):
		#Concatenate all sentences from all paragraphs in an aligned node:
		text = []
		for index in aligned_nodes:
			for sentence in paragraphs[index]:
				text.append(sentence.strip())
		return text

####################################################################################################################################################
			
class VicinityDrivenSentenceAligner(SentenceAligner):

	def __init__(self, similarity_model=None, acceptable_similarity=0.2, similarity_slack=0.05):
		self.total_vicinity = set([(1,1),(1,0),(0,1),(2,1),(1,2)])
		self.first_vicinity = set([(1,1),(1,0),(0,1)])
		self.second_vicinity = set([(1,2),(2,1)])
		self.acceptable_similarity = acceptable_similarity
		self.similarity_slack = similarity_slack
		self.similarity_model = similarity_model
		
	def alignSentencesFromParagraphs(self, p1=[], p2=[]):
		#Get similarity model:
		sentence_similarities, sentence_indexes = self.similarity_model.getSimilarityMapBetweenSentencesOfParagraphs(p1, p2)
		
		#Calculate alignment path:
		path = self.getSentenceAlignmentPath(p1, p2, sentence_similarities, sentence_indexes)
		
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
	
	def getSentenceAlignmentPath(self, p1, p2, sentence_similarities, sentence_indexes):
		#Get paragraph sizes:
		sizep1 = len(p1)
		sizep2 = len(p2)
		
		#Start vicinity-driven path search:
		matrix = self.getProbabilityMatrix(p1, p2, sentence_similarities, sentence_indexes)
		
		#Build alignment path:
		path = []
		cbuffer = ''
		sbuffer = ''
		starting_point = self.findStartingPoint(matrix, p1, p2, [-1,-1])
		if starting_point[0]>=len(p1) or starting_point[1]>=len(p2):
			return [], []
		
		currXY = starting_point
		cbuffer = p1[currXY[0]]
		final_cbuffer = [currXY[0]]
		sbuffer = p2[currXY[1]]
		final_sbuffer = [currXY[1]]
		while currXY[0]<len(p1)-1 and currXY[1]<len(p2)-1:
			bestNextXY, bestNextXYProb = self.getBestNextHypothesis(matrix, p1, p2, cbuffer, sbuffer, currXY)
			#Check to see if best is diagonal:
			if bestNextXY[0]==currXY[0]+1 and bestNextXY[1]==currXY[1]+1:
				path.append((final_cbuffer, final_sbuffer))
				currXY = bestNextXY
				cbuffer = p1[currXY[0]]
				final_cbuffer = [currXY[0]]
				sbuffer = p2[currXY[1]]
				final_sbuffer = [currXY[1]]
			#Check to see if downards is best:
			elif bestNextXY[0]==currXY[0]+1 and bestNextXY[1]==currXY[1]:
				anchor = bestNextXY[0]+1
				prevsim = self.similarity_model.getTextSimilarity(cbuffer, sbuffer)
				cbuffer += ' ' + p1[bestNextXY[0]]
				final_cbuffer.append(bestNextXY[0])
				currsim = bestNextXYProb
				while anchor<len(p1) and currsim>matrix[anchor][bestNextXY[1]+1] and currsim>prevsim-self.similarity_slack:
					anchor += 1
					if anchor<len(p1):
						prevsim = currsim
						currsim = self.similarity_model.getTextSimilarity(cbuffer+' '+p1[anchor], sbuffer)
						if currsim>prevsim-self.similarity_slack and currsim>matrix[anchor][bestNextXY[1]+1]:
							cbuffer += ' ' + p1[anchor]
							final_cbuffer.append(anchor)
						else:
							anchor -= 1
							currsim = 0.0
				path.append((final_cbuffer, final_sbuffer))
				if anchor<len(p1):
					currXY = self.findStartingPoint(matrix, p1, p2, [anchor-1, bestNextXY[1]])
					if currXY[0]<len(p1) and currXY[1]<len(p2):
						cbuffer = p1[currXY[0]]
						final_cbuffer = [currXY[0]]
						sbuffer = p2[currXY[1]]
						final_sbuffer = [currXY[1]]
				else:
					currXY = (anchor, bestNextXY[1]+1)
			elif  bestNextXY[0]==currXY[0] and bestNextXY[1]==currXY[1]+1:
				anchor = bestNextXY[1]+1
				prevsim = self.similarity_model.getTextSimilarity(cbuffer, sbuffer)
				sbuffer += ' ' + p2[bestNextXY[1]]
				final_sbuffer.append(bestNextXY[1])
				currsim = bestNextXYProb
				while anchor<len(p2) and currsim>matrix[bestNextXY[0]+1][anchor] and currsim>prevsim-self.similarity_slack:
					anchor += 1
					if anchor<len(p2):
						prevsim = currsim
						currsim = self.similarity_model.getTextSimilarity(cbuffer, sbuffer+' '+p2[anchor])
						if currsim>prevsim-self.similarity_slack and currsim>matrix[bestNextXY[0]+1][anchor]:
							sbuffer += ' ' + p2[anchor]
							final_sbuffer.append(anchor)
						else:
							anchor -= 1
							currsim = 0.0
				path.append((final_cbuffer, final_sbuffer))
				if anchor<len(p2):
					currXY = self.findStartingPoint(matrix, p1, p2, [bestNextXY[0], anchor-1])
					if currXY[0]<len(p1) and currXY[1]<len(p2):
						cbuffer = p1[currXY[0]]
						final_cbuffer = [currXY[0]]
						sbuffer = p2[currXY[1]]
						final_sbuffer = [currXY[1]]
				else:
					currXY = (bestNextXY[0]+1, anchor)
			else:
				path.append((final_cbuffer, final_sbuffer))
				currXY = bestNextXY
				if bestNextXY[0]<len(p1) and bestNextXY[1]<len(p2):
					cbuffer = p1[currXY[0]]
					final_cbuffer = [currXY[0]]
					sbuffer = p2[currXY[1]]
					final_sbuffer = [currXY[1]]

		if currXY[0]<len(p1) and currXY[1]<len(p2) and self.similarity_model.getTextSimilarity(cbuffer, sbuffer)>self.acceptable_similarity:
			#In case last alignment is in the very corner:			
			if currXY[0]==len(p1)-1 and currXY[1]==len(p2)-1:
				path.append((final_cbuffer, final_sbuffer))
			#In case last alignment is in the last line:
			elif currXY[0]==len(p1)-1:
				prevsim = -9999
				anchor = currXY[1]
				currsim = self.similarity_model.getTextSimilarity(cbuffer, sbuffer)
				while anchor<len(p2) and currsim>=prevsim-self.similarity_slack:
					if anchor<len(p2)-1:
						prevsim = currsim
						currsim = self.similarity_model.getTextSimilarity(cbuffer, sbuffer+' '+p2[anchor+1])
						if currsim>=prevsim-self.similarity_slack:
							sbuffer += ' ' + p2[anchor+1]
							final_sbuffer.append(anchor+1)
					anchor += 1
				path.append((final_cbuffer, final_sbuffer))
			else:
				prevsim = -9999
				anchor = currXY[0]
				currsim = self.similarity_model.getTextSimilarity(cbuffer, sbuffer)
				while anchor<len(p1) and currsim>=prevsim-self.similarity_slack:
					if anchor<len(p1)-1:
						prevsim = currsim
						currsim = self.similarity_model.getTextSimilarity(cbuffer+' '+p1[anchor+1], sbuffer)
						if currsim>=prevsim-self.similarity_slack:
							cbuffer += ' ' + p1[anchor+1]
							final_cbuffer.append(anchor+1)
					anchor += 1
				path.append((final_cbuffer, final_sbuffer))
		return path
		
	def findStartingPoint(self, matrix, p1, p2, startpos):
		sizec = len(p1)
		sizes = len(p2)
		visited = set([])
		currdist = 0
		if startpos[0]>-1 and startpos[1]>-1:
			currdist = startpos[0]+startpos[1]
		currpos = [int(startpos[0]), int(startpos[1])]
		found = False
		reached_end = False
		while not found and not reached_end:
			if currpos[0]==-1 and currpos[1]==-1:
				currpos = [0, 0]
			else:
				if currpos[0]==0:
					currdist += 1
					currpos = [currdist, 0]
				else:
					currpos[0] -= 1
					currpos[1] += 1
			if (sizec-1, sizes-1) in visited:
				reached_end = True
			else:
				if currpos[0]<sizec and currpos[1]<sizes and matrix[currpos[0],currpos[1]]>=self.acceptable_similarity and matrix[currpos[0],currpos[1]]<1.1:
					if currpos[0]>=startpos[0] and currpos[1]>=startpos[1]:
						found = True
			visited.add((currpos[0], currpos[1]))
		if reached_end:
			return [sizec,sizes]
		else:
			return currpos
			
	def getBestNextHypothesis(self, matrix, p1, p2, cbuffer, sbuffer, currXY):
		#Test diagonal:
		diag = (currXY[0]+1, currXY[1]+1)
		diagsim = matrix[currXY[0]+1][currXY[1]+1]
		prevsim = matrix[currXY[0]][currXY[1]]

		#Test downwards:
		downText = cbuffer + ' ' + p1[currXY[0]+1]
		downsim = self.similarity_model.getTextSimilarity(downText, sbuffer)
		down = (currXY[0]+1, currXY[1])
		if downsim<=prevsim-self.similarity_slack:
			downsim = 0.0

		#Test rightwards:
		rightText = sbuffer + ' ' + p2[currXY[1]+1]
		rightsim = self.similarity_model.getTextSimilarity(cbuffer, rightText)
		right = (currXY[0], currXY[1]+1)
		if rightsim<=prevsim-self.similarity_slack:
			rightsim = 0.0

		coordinates = [diag, down, right]
		sims = [diagsim, downsim, rightsim]

		maxvalue = np.max(sims)
		if maxvalue>=self.acceptable_similarity:
			result = np.argmax(sims)
			coordinate = coordinates[result]
			prob = sims[result]
			return coordinate, prob
		else:
			newc = self.findStartingPoint(matrix, p1, p2, currXY)
			newp = matrix[newc[0]][newc[1]]
			return newc, newp
	
	def getProbabilityMatrix(self, p1, p2, sentence_similarities, sentence_indexes):
		#Start the creation of the regularized search matrix:
		sizec = len(p1)
		sizes = len(p2)
		maxsize = np.max([sizec, sizes])
		final_matrix = np.zeros((maxsize+1, maxsize+1))
		
		#Fill regularized search matrix:
		for i in range(sizec, maxsize+1):
			for j in range(0, maxsize+1):
				final_matrix[i][j] = 99999
		for j in range(sizes, maxsize+1):
			for i in range(0, maxsize+1):
				final_matrix[i][j] = 99999
		for i, s1 in enumerate(p1):
			for j, s2 in enumerate(p2):
				final_matrix[i][j] = sentence_similarities[sentence_indexes[s1]][sentence_indexes[s2]]

		#Return regularized search matrix:
		return final_matrix
		
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
