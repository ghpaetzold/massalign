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
	"""
	Implements the vicinity-driven paragraph alignment algorithm proposed in:
	
		Gustavo H. Paetzold and Lucia Specia. **Vicinity-Driven Paragraph and Sentence Alignment for Comparable Corpora**. *arXiv preprint arXiv:1612.04113* (2016).
		
	* *Parameters*:
		* **similarity_model**: An instance of a class deriving from SimilarityModel.
		* **acceptable_similarity**: The minimum similarity score between two paragraphs necessary for an alignment to be considered.
	"""

	def __init__(self, similarity_model=None, acceptable_similarity=0.3):
		self.total_vicinity = set([(1,1),(1,0),(0,1),(2,1),(1,2)])
		self.first_vicinity = set([(1,1),(1,0),(0,1)])
		self.second_vicinity = set([(1,2),(2,1)])
		self.acceptable_similarity = acceptable_similarity
		self.similarity_model = similarity_model
		
	def alignParagraphsFromDocuments(self, p1s=[], p2s=[]):
		"""
		Finds alignments between a list of source and target paragraphs that compose a pair of comparable documents.
		To do so, it produces a similarity matrix between the paragraphs in the source and target list, then finds an alignment path within it using a vicinity-driven approach.
		
		* *Parameters*:
			* **p1s**: A list of source paragraphs. Each paragraph is a list of sentences.
			* **p2s**: A list of target paragraphs. Each paragraph is a list of sentences.
		* *Output*:
			* **alignment_path**: A list of coordinates in the similarity matrix that describes which paragraphs are aligned.
			* **aligned_paragraphs**: A list containing all pairs of aligned paragraphs.
		"""
		#Get similarity model:
		paragraph_similarities = self.similarity_model.getSimilarityMapBetweenParagraphsOfDocuments(p1s, p2s)
		
		#Calculate alignment path:
		alignment_path = self.getParagraphAlignmentPath(p1s, p2s, paragraph_similarities)
		
		#Produce actual alignments:
		aligned_paragraphs = self.getActualAlignedParagraphs(p1s, p2s, alignment_path)
		
		#Return alignment path:
		return alignment_path, aligned_paragraphs
		
	def getParagraphAlignmentPath(self, p1s, p2s, paragraph_similarities):
		"""
		Searches for the alignment path in a matrix containing similarity scores for all paragraph pairs.
		
		* *Parameters*:
			* **p1s**: A list of source paragraphs. Each paragraph is a list of sentences.
			* **p2s**: A list of target paragraphs. Each paragraph is a list of sentences.
			* **paragraph_similarities**: A matrix of dimensions [length(p1s),length(p2s)] containing a similarity score for each paragraph pair.
		* *Output*:
			* **compact_path**: A list of coordinates in the similarity matrix that describes which paragraphs are aligned.
		"""
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
		"""
		Searches for the next alignment during the search for the alignment path.
		
		* *Parameters*:
			* **currXY**: Current coordinate in the similarity matrix from which to continue the search.
			* **paragraph_similarities**: A matrix containing a similarity score for each paragraph pair.
		* *Output*:
			* **x, y**: The coordinate for the next alignment.
		"""
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
		"""
		If it was impossible to find any suitable alignments within the vicinities specified, then search for the acceptable alignment outside the vicinities that is closest to the current search coordinate.
		
		* *Parameters*:
			* **currXY**: Current coordinate in the similarity matrix from which to continue the search.
			* **paragraph_similarities**: A matrix containing a similarity score for each paragraph pair.
		* *Output*:
			* **x, y**: The coordinate for the next acceptable alignment outside the valid vicinities.
		"""
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
		"""
		Produces a convenient list containing the pairs of aligned paragraphs found between two lists of paragraphs.
		It concatenates all paragraphs in the "N" side of 1-N and N-1 alignments.
		
		* *Parameters*:
			* **p1s**: A list of source paragraphs. Each paragraph is a list of sentences.
			* **p2s**: A list of target paragraphs. Each paragraph is a list of sentences.
			* **alignment_path**: A list of coordinates in the similarity matrix that describes which paragraphs are aligned.
		* *Output*:
			* **aligned_paragraphs**: A list containing all pairs of aligned paragraphs.
		"""
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
		"""
		Concatenates all paragraphs in a 1-N or N-1 alignment.
		
		* *Parameters*:
			* **aligned_nodes**: A list of paragraph indexes from a node in the alignment path.
			* **paragraphs**: A list of paragraphs. Each paragraph is a list of sentences.
		* *Output*:
			* **text**: A list of all the paragraphs in the aligned nodes.
		"""
		#Concatenate all sentences from all paragraphs in an aligned node:
		text = []
		for index in aligned_nodes:
			for sentence in paragraphs[index]:
				text.append(sentence.strip())
		return text

####################################################################################################################################################
			
class VicinityDrivenSentenceAligner(SentenceAligner):
	"""
	Implements the vicinity-driven sentence alignment algorithm proposed in:
	
		Gustavo H. Paetzold and Lucia Specia. **Vicinity-Driven Paragraph and Sentence Alignment for Comparable Corpora**. *arXiv preprint arXiv:1612.04113* (2016).
		
	* *Parameters*:
		* **similarity_model**: An instance of a class deriving from SimilarityModel.
		* **acceptable_similarity**: The minimum similarity score between two paragraphs necessary for an alignment to be considered.
		* **similarity_slack**: The maximum amount of similarity that can be lost after each step of incrementing N when finding for a 1-N or N-1 alignment.
	"""

	def __init__(self, similarity_model=None, acceptable_similarity=0.2, similarity_slack=0.05):
		self.total_vicinity = set([(1,1),(1,0),(0,1),(2,1),(1,2)])
		self.first_vicinity = set([(1,1),(1,0),(0,1)])
		self.second_vicinity = set([(1,2),(2,1)])
		self.acceptable_similarity = acceptable_similarity
		self.similarity_slack = similarity_slack
		self.similarity_model = similarity_model
		
	def alignSentencesFromParagraphs(self, p1=[], p2=[]):
		"""
		Finds alignments between a list of source and target sentences that compose a pair of aligned paragraphs.
		To do so, it produces a similarity matrix between the sentences in the source and target sentences, then finds an alignment path within it using a vicinity-driven approach.
		
		* *Parameters*:
			* **p1**: A source paragraph. A paragraph is a list of sentences.
			* **p2**: A target paragraph. A paragraph is a list of sentences.
		* *Output*:
			* **alignment_path**: A list of coordinates in the similarity matrix that describes which sentences are aligned.
			* **aligned_sentences**: A list containing all pairs of aligned sentences.
		"""
		#Get similarity model:
		sentence_similarities, sentence_indexes = self.similarity_model.getSimilarityMapBetweenSentencesOfParagraphs(p1, p2)
		
		#Calculate alignment path:
		alignment_path = self.getSentenceAlignmentPath(p1, p2, sentence_similarities, sentence_indexes)

		#Produce actual alignments:
		aligned_sentences = self.getActualAlignedSentences(p1, p2, alignment_path)
		
		#Return alignment path:
		return alignment_path, aligned_sentences
	
	def getSentenceAlignmentPath(self, p1, p2, sentence_similarities, sentence_indexes):
		"""
		Produces a similarity matrix and searches for the alignment path within it.
		
		* *Parameters*:
			* **p1**: A source paragraph. A paragraph is a list of sentences.
			* **p2**: A target paragraph. A paragraph is a list of sentences.
			* **sentence_similarities**: A matrix containing a similarity score between all possible pairs of sentences in the union of p1 and p2. The matrix's height and width are equal and equivalent to the number of distinct sentences present in the union of p1 and p2.
			* **sentence_indexes**: A map connecting each sentence to its numerical index in the sentence_similarities matrix.
		* *Output*:
			* **path**: A list of coordinates in the similarity matrix that describes which sentences are aligned.
		"""
		#Get paragraph sizes:
		sizep1 = len(p1)
		sizep2 = len(p2)
		
		#Start vicinity-driven path search:
		matrix = self.getProbabilityMatrix(p1, p2, sentence_similarities, sentence_indexes)
		
		#Start search for alignment path:
		path = []
		cbuffer = ''
		sbuffer = ''
		starting_point = self.findStartingPoint(matrix, p1, p2, [-1,-1])
		if starting_point[0]>=len(p1) or starting_point[1]>=len(p2):
			return [], []
		currXY = starting_point
		
		#Instantiate buffers:
		cbuffer = p1[currXY[0]]
		final_cbuffer = [currXY[0]]
		sbuffer = p2[currXY[1]]
		final_sbuffer = [currXY[1]]
		
		#While the edge of the similarity matrix is not reached, do:
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
				#Keep moving downards until the alignment stops improving:
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
				
				#If edge is not reached, find new starting point to continue the alignment search:
				if anchor<len(p1):
					currXY = self.findStartingPoint(matrix, p1, p2, [anchor-1, bestNextXY[1]])
					if currXY[0]<len(p1) and currXY[1]<len(p2):
						cbuffer = p1[currXY[0]]
						final_cbuffer = [currXY[0]]
						sbuffer = p2[currXY[1]]
						final_sbuffer = [currXY[1]]
				#Otherwise, move along the edge in the opposite axis:
				else:
					currXY = (anchor, bestNextXY[1]+1)
					
			#Check to see if rightwards is best:
			elif  bestNextXY[0]==currXY[0] and bestNextXY[1]==currXY[1]+1:
				#Keep moving rightwards until the alignment stops improving:
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
				
				#If edge is not reached, find new starting point to continue the alignment search:
				if anchor<len(p2):
					currXY = self.findStartingPoint(matrix, p1, p2, [bestNextXY[0], anchor-1])
					if currXY[0]<len(p1) and currXY[1]<len(p2):
						cbuffer = p1[currXY[0]]
						final_cbuffer = [currXY[0]]
						sbuffer = p2[currXY[1]]
						final_sbuffer = [currXY[1]]
				#Otherwise, move along the edge in the opposite axis:
				else:
					currXY = (bestNextXY[0]+1, anchor)
			
			#Check if moving diagonally is best:
			else:
				path.append((final_cbuffer, final_sbuffer))
				currXY = bestNextXY
				if bestNextXY[0]<len(p1) and bestNextXY[1]<len(p2):
					cbuffer = p1[currXY[0]]
					final_cbuffer = [currXY[0]]
					sbuffer = p2[currXY[1]]
					final_sbuffer = [currXY[1]]

		#Continue search from the very edge:
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
		"""
		Searches for a coordinate in the similarity matrix from which to start (or recover) the alignment path search.
		
		* *Parameters*:
			* **matrix**:  A matrix of dimensions [length(p1),length(p2)] containing a similarity score for each sentence pair.
			* **p1**: A source paragraph. A paragraph is a list of sentences.
			* **p2**: A target paragraph. A paragraph is a list of sentences.
			* **startpos**: The coordinate from which to start the search for the first alignment in the matrix (usually [-1,-1]).
		* *Output*:
			* **x, y**: The coordinate of the next alignment in the similarity matrix.
		"""
		#Start search for starting point:
		sizec = len(p1)
		sizes = len(p2)
		visited = set([])
		currdist = 0
		if startpos[0]>-1 and startpos[1]>-1:
			currdist = startpos[0]+startpos[1]
		currpos = [int(startpos[0]), int(startpos[1])]
		found = False
		reached_end = False
		
		#Do a search on a per-distance basis until a good enough pair is found:
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
		
		#If no pairs are similar enough, return last position in the matrix:
		if reached_end:
			return [sizec,sizes]
		#Otherwise, return the position found:
		else:
			return currpos
			
	def getBestNextHypothesis(self, matrix, p1, p2, cbuffer, sbuffer, currXY):
		"""
		Searches for the next alignment in the alignment matrix.
		
		* *Parameters*:
			* **matrix**:  A matrix of dimensions [length(p1),length(p2)] containing a similarity score for each sentence pair.
			* **p1**: A source paragraph. A paragraph is a list of sentences.
			* **p2**: A target paragraph. A paragraph is a list of sentences.
			* **cbuffer**: The concatenation of all aligned sentences in the source side, in case the current alignment is of N-1 kind.
			* **sbuffer**: The concatenation of all aligned sentences in the target side, in case the current alignment is of 1-N kind.
			* **currXY**: Current coordinate in the similarity matrix from which to continue the search.
		* *Output*:
			* **x, y**: A coordinate in the similarity matrix that represents the next alignment in the alignment path.
		"""
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

		#Summarize simliarities:
		coordinates = [diag, down, right]
		sims = [diagsim, downsim, rightsim]

		#If there is a good enough candidate, return it:
		maxvalue = np.max(sims)
		if maxvalue>=self.acceptable_similarity:
			result = np.argmax(sims)
			coordinate = coordinates[result]
			prob = sims[result]
			return coordinate, prob
		#If not, find another one outside the vicinity:
		else:
			newc = self.findStartingPoint(matrix, p1, p2, currXY)
			newp = matrix[newc[0]][newc[1]]
			return newc, newp
	
	def getProbabilityMatrix(self, p1, p2, sentence_similarities, sentence_indexes):
		"""
		Produces a similarity matrix between the sentences in the aligned paragraphs
		
		* *Parameters*:
			* **p1**: A source paragraph. A paragraph is a list of sentences.
			* **p2**: A target paragraph. A paragraph is a list of sentences.
			* **sentence_similarities**: A matrix containing a similarity score between all possible pairs of sentences in the union of p1 and p2. The matrix's height and width are equal and equivalent to the number of distinct sentences present in the union of p1 and p2.
			* **sentence_indexes**: A map connecting each sentence to its numerical index in the sentence_similarities matrix.
		* *Output*:
			* **matrix**: A similarity matrix with dimensions [length(p1),length(p2)]
		"""
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
		
	def getActualAlignedSentences(self, p1, p2, alignment_path):
		"""
		Produces a convenient list containing the pairs of aligned sentences found between two paragraphs.
		It concatenates all sentences in the "N" side of 1-N and N-1 alignments.
		
		* *Parameters*:
			* **p1**: A source paragraph. A paragraph is a list of sentences.
			* **p2**: A target paragraph. A paragraph is a list of sentences.
			* **alignment_path**: A list of coordinates in the similarity matrix that describes which sentences are aligned.
		* *Output*:
			* **aligned_sentences**: A list containing all pairs of aligned sentences.
		"""
		#Create structure to store aligned sentences:
		aligned_sentences = []
		
		#For each alignment in the path, produce final aligned text of both sides:
		for node in alignment_path:
			if len(node)>1:
				s1 = self.getOriginalSentence(node[0], p1)
				s2 = self.getOriginalSentence(node[1], p2)
				aligned_sentences.append([s1, s2])
		
		#Return aligned sentences:
		return aligned_sentences
	
	def getOriginalSentence(self, indexes, p):
		"""
		Concatenates a list of sentences.
		
		* *Parameters*:
			* **indexes**: A list of indexes of sentences in a paragraph
			* **paragraphs**: A paragraph. A paragraph is a list of sentences.
		* *Output*:
			* **sentence**: A concatenation of all sentences.
		"""
		#Allocate sentence:
		sentence = ''
		
		#Add aligned sentences to resulting sentence:
		for index in indexes:
			sentence += p[index] + ' '
			
		#Return resulting sentence:
		return sentence.strip()
