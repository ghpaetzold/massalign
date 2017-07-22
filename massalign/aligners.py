from abc import ABCMeta, abstractmethod

class ParagraphAligner:

    __metaclass__ = ABCMeta

    @abstractmethod
    def alignParagraphsFromDocuments(self):
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
		path = getParagraphAlignmentPath(p1s, p2s, paragraph_similarities)
		
		#Return alignment path:
		return path
		
	def getSentenceMap(self, paragraphs):
		map = {}
		for i, p in enumerate(paragraphs):
			for sentence in p:
				if sentence not in map:
					map[sentence] = set([])
				map[sentence].add(i)
		return map
		
	def getParagraphAlignmentPath(self, p1s, p2s, paragraph_similarities):
		#Get paragraph sizes:
		sizep1 = len(p1s)
		sizep2 = len(p2s)
		
		path = [(0, 0)]
		currXY = (0, 0)
		while currXY[0]<sizep1-1 or currXY[1]<sizep2-1:
			nextXY, nextXYsim = self.getNextAlignment(currXY, paragraph_similarities)
			if nextXY[0]==sizep1-1 and nextXY[1]==sizep2-1:
				if nextXYsim>=0.3:
					path.append(nextXY)
			else:
				path.append(nextXY)
			currXY = nextXY

		for j, node in enumerate(path):
			path[j] = [[node[0]],[node[1]]]

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
		return compact_path
		
	def getNextAlignment(self, currXY, paragraph_similarities):
		cands = {}
		for pos in self.total_vicinity:
			candXY = (currXY[0]+pos[0], currXY[1]+pos[1])
			sim = -99999
			try:
				sim = paragraph_similarities[candXY[0]][candXY[1]]
			except Exception:
				pass
			cands[candXY] = sim
		winners = sorted(cands.keys(), key=cands.__getitem__, reverse=True)

		nearest = [cands[(currXY[0]+pos[0], currXY[1]+pos[1])] for pos in self.first_vicinity]
		if np.max(nearest)>=self.acceptable_similarity:
			auxes = [(currXY[0]+pos[0], currXY[1]+pos[1]) for pos in self.second_vicinity]
			for aux in auxes:
					winners.remove(aux)
			return winners[0], cands[winners[0]]
		else:
			all = [cands[c] for c in cands]
			if np.max(all)<self.acceptable_similarity:
				finalNextXY = self.getNextSynchronizer(currXY, paragraph_similarities)
				return finalNextXY, paragraph_similarities[finalNextXY[0]][finalNextXY[1]]
			else:
				return winners[0], cands[winners[0]]

	def getNextSynchronizer(self, currXY, paragraph_similarities):
		cands = {}
		orig = currXY
		last = [len(paragraph_similarities), len(paragraph_similarities[0])]
		for i in range(orig[0], last[0]):
			for j in range(orig[1], last[1]):
				if i!=orig[0] and j!=orig[1] and paragraph_similarities[i][j]>=self.acceptable_similarity:
					cands[(i, j)] = (i-orig[0])+(j-orig[1])
		if len(cands)>0:
			closest = sorted(cands.keys(), key=cands.__getitem__)
			return closest[0]
		else:
			return (last[0]-1, last[1]-1)