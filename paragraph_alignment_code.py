import os, gensim
import numpy as np
from nltk.util import ngrams

def getFinalSentenceAlignments(sent_path):
	map = {}
	for node in sent_path:
		c = node[0]
		s = node[1]
		if c not in map:
			map[c] = ''
		map[c] += ' ' + s
	for c in map:
		map[c] = map[c].strip()
	return map

def getSimilarity(cbuffer, sbuffer, dictionary, tfidf):
	cvec = dictionary.doc2bow(cbuffer.split())
        svec = dictionary.doc2bow(sbuffer.split())
	corpus = [cvec, svec]
	index = gensim.similarities.MatrixSimilarity(tfidf[corpus])
	sims = index[tfidf[cvec]]
	return sims[1]

def getBestNextHypothesis(matrix, all_complex, all_simple, cbuffer, sbuffer, currXY, dictionary, tfidf, minvalue, prevslack):
	#Test diagonal:
	diag = (currXY[0]+1, currXY[1]+1)
	diagsim = matrix[currXY[0]+1][currXY[1]+1]

	#Test downwards:
	prevsim = matrix[currXY[0]][currXY[1]]
	downText = cbuffer + ' ' + all_complex[currXY[0]+1]
	cvec = dictionary.doc2bow(downText.split())
	svec = dictionary.doc2bow(sbuffer.split())
	corpus = [cvec, svec]
	downsim = 0.0
	try:
		index = gensim.similarities.MatrixSimilarity(tfidf[corpus])
		sims = index[tfidf[cvec]]
		downsim = sims[1]
	except Exception:
		downsim = 0.0
	down = (currXY[0]+1, currXY[1])
	if downsim<=prevsim-prevslack:
		downsim = 0.0

	#Test rightwards:
	rightText = sbuffer + ' ' + all_simple[currXY[1]+1]
	svec = dictionary.doc2bow(rightText.split())
	cvec = dictionary.doc2bow(cbuffer.split())
	corpus = [svec, cvec]
	rightsim = 0.0
	try:
		index = gensim.similarities.MatrixSimilarity(tfidf[corpus])
		sims = index[tfidf[svec]]
		rightsim = sims[1]
	except Exception:
		rightsim = 0.0
	right = (currXY[0], currXY[1]+1)
	if rightsim<=prevsim-prevslack:
		rightsim = 0.0

	coordinates = [diag, down, right]
	sims = [diagsim, downsim, rightsim]

#	print(str(coordinates) + ' - ' + str(sims))

	maxvalue = np.max(sims)
	if maxvalue>=minvalue:
		result = np.argmax(sims)
		coordinate = coordinates[result]
		prob = sims[result]
		return coordinate, prob
	else:
		newc = findStartingPoint(matrix, all_complex, all_simple, minvalue, currXY)
		newp = matrix[newc[0]][newc[1]]
		return newc, newp

def findStartingPoint(matrix, all_complex, all_simple, minvalue, startpos):
	sizec = len(all_complex)
	sizes = len(all_simple)
	visited = set([])
	currdist = 0
	if startpos[0]>-1 and startpos[1]>-1:
		currdist = startpos[0]+startpos[1]
	currpos = [int(startpos[0]), int(startpos[1])]
#	print('Started at: ' + str(currpos))
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
			if currpos[0]<sizec and currpos[1]<sizes and matrix[currpos[0],currpos[1]]>=minvalue and matrix[currpos[0],currpos[1]]<1.1:
				if currpos[0]>=startpos[0] and currpos[1]>=startpos[1]:
					found = True
		visited.add((currpos[0], currpos[1]))
#		print('Currpos before loop ends: ' + str(currpos))
	if reached_end:
		return [sizec,sizes]
	else:
#		print('We found: ' + str(currpos))
		return currpos

def getSentenceAlignmentPath(matrix, all_complex, all_simple, dictionary, tfidf, minvalue, prevslack):
	path = []
	steps = []
	cbuffer = ''
	sbuffer = ''
	starting_point = findStartingPoint(matrix, all_complex, all_simple, minvalue, [-1,-1])
	steps.append('Started at: ' + str(starting_point))
	if starting_point[0]>=len(all_complex) or starting_point[1]>=len(all_simple):
#	if matrix[starting_point[0]][starting_point[1]]<minvalue:
		return [], []
	
	currXY = starting_point
	cbuffer = all_complex[currXY[0]]
	sbuffer = all_simple[currXY[1]]
	while currXY[0]<len(all_complex)-1 and currXY[1]<len(all_simple)-1:
		bestNextXY, bestNextXYProb = getBestNextHypothesis(matrix, all_complex, all_simple, cbuffer, sbuffer, currXY, dictionary, tfidf, minvalue, prevslack)
		#Check to see if best is diagonal:
		if bestNextXY[0]==currXY[0]+1 and bestNextXY[1]==currXY[1]+1:
			steps.append('Found best diagonal next: ' + str(bestNextXY))
			path.append((cbuffer, sbuffer))
			currXY = bestNextXY
			cbuffer = all_complex[currXY[0]]
			sbuffer = all_simple[currXY[1]]
		#Check to see if downards is best:
		elif bestNextXY[0]==currXY[0]+1 and bestNextXY[1]==currXY[1]:
			anchor = bestNextXY[0]+1
			prevsim = getSimilarity(cbuffer, sbuffer, dictionary, tfidf)
			cbuffer += ' ' + all_complex[bestNextXY[0]]
			currsim = bestNextXYProb
			steps.append('Found best downwards next: ' + str(bestNextXY) + ', currism : ' + str(currsim) + ', prevsim: ' + str(prevsim))
			while anchor<len(all_complex) and currsim>matrix[anchor][bestNextXY[1]+1] and currsim>prevsim-prevslack:
				anchor += 1
				if anchor<len(all_complex):
					prevsim = currsim
					currsim = getSimilarity(cbuffer+' '+all_complex[anchor], sbuffer, dictionary, tfidf)
					if currsim>prevsim-prevslack and currsim>matrix[anchor][bestNextXY[1]+1]:
						steps.append('\tDownwards to ' + str((anchor, bestNextXY[1])) + ' from ' + str(prevsim) + ' to ' + str(currsim))
						cbuffer += ' ' + all_complex[anchor]
					else:
						if currsim<=prevsim-prevslack:
							steps.append('\tStopped because currsim: ' + str(currsim) + ', prevsim: ' + str(prevsim))
						else:
							steps.append('\tStopped because currsim: ' + str(currsim) + ', diagonal: ' + str(matrix[anchor][bestNextXY[1]+1]))
						anchor -= 1
						currsim = 0.0
			path.append((cbuffer, sbuffer))
#			currXY = (anchor, bestNextXY[1]+1)
			if anchor<len(all_complex):
				currXY = findStartingPoint(matrix, all_complex, all_simple, minvalue, [anchor-1, bestNextXY[1]])
				if currXY[0]<len(all_complex) and currXY[1]<len(all_simple):
					cbuffer = all_complex[currXY[0]]
					sbuffer = all_simple[currXY[1]]
			else:
				currXY = (anchor, bestNextXY[1]+1)
		elif  bestNextXY[0]==currXY[0] and bestNextXY[1]==currXY[1]+1:
			anchor = bestNextXY[1]+1
			prevsim = getSimilarity(cbuffer, sbuffer, dictionary, tfidf)
                        sbuffer += ' ' + all_simple[bestNextXY[1]]
			currsim = bestNextXYProb
			steps.append('Found best rightwards next: ' + str(bestNextXY) + ', currism : ' + str(currsim) + ', prevsim: ' + str(prevsim))
			while anchor<len(all_simple) and currsim>matrix[bestNextXY[0]+1][anchor] and currsim>prevsim-prevslack:
                                anchor += 1
				if anchor<len(all_simple):
	                                prevsim = currsim
	                                currsim = getSimilarity(cbuffer, sbuffer+' '+all_simple[anchor], dictionary, tfidf)
					if currsim>prevsim-prevslack and currsim>matrix[bestNextXY[0]+1][anchor]:
						steps.append('\tRightwards to ' + str((bestNextXY[0],anchor)) + ' from ' + str(prevsim) + ' to ' + str(currsim))
						sbuffer += ' ' + all_simple[anchor]
					else:
						if currsim<=prevsim-prevslack:
                                                        steps.append('\tStopped because currsim: ' + str(currsim) + ', prevsim: ' + str(prevsim))
                                                else:
                                                        steps.append('\tStopped because currsim: ' + str(currsim) + ', diagonal: ' + str(matrix[bestNextXY[0]+1][anchor]))
						anchor -= 1
						currsim = 0.0
                        path.append((cbuffer, sbuffer))
#                        currXY = (bestNextXY[0]+1, anchor)
                        if anchor<len(all_simple):
				currXY = findStartingPoint(matrix, all_complex, all_simple, minvalue, [bestNextXY[0], anchor-1])
				if currXY[0]<len(all_complex) and currXY[1]<len(all_simple):
	                                cbuffer = all_complex[currXY[0]]
	                                sbuffer = all_simple[currXY[1]]
			else:
				currXY = (bestNextXY[0]+1, anchor)
		else:
			steps.append('Found new starting point: ' + str(bestNextXY))
                        path.append((cbuffer, sbuffer))
                        currXY = bestNextXY
			if bestNextXY[0]<len(all_complex) and bestNextXY[1]<len(all_simple):
	                        cbuffer = all_complex[currXY[0]]
	                        sbuffer = all_simple[currXY[1]]

	if currXY[0]<len(all_complex) and currXY[1]<len(all_simple) and getSimilarity(cbuffer, sbuffer, dictionary, tfidf)>minvalue:
		#In case last alignment is in the very corner:			
		if currXY[0]==len(all_complex)-1 and currXY[1]==len(all_simple)-1:
			path.append((cbuffer, sbuffer))
		#In case last alignment is in the last line:
		elif currXY[0]==len(all_complex)-1:
			prevsim = -9999
			anchor = currXY[1]
			currsim = getSimilarity(cbuffer, sbuffer, dictionary, tfidf)
			while anchor<len(all_simple) and currsim>=prevsim-prevslack:
				if anchor<len(all_simple)-1:
					prevsim = currsim
					currsim = getSimilarity(cbuffer, sbuffer+' '+all_simple[anchor+1], dictionary, tfidf)
					if currsim>=prevsim-prevslack:
						sbuffer += ' ' + all_simple[anchor+1]
				anchor += 1
			path.append((cbuffer, sbuffer))
		else:
			prevsim = -9999
                        anchor = currXY[0]
                        currsim = getSimilarity(cbuffer, sbuffer, dictionary, tfidf)
                        while anchor<len(all_complex) and currsim>=prevsim-prevslack:
                                if anchor<len(all_complex)-1:
                                        prevsim = currsim
                                        currsim = getSimilarity(cbuffer+' '+all_complex[anchor+1], sbuffer, dictionary, tfidf)
                                        if currsim>=prevsim-prevslack:
                                                cbuffer += ' ' + all_complex[anchor+1]
                                anchor += 1
                        path.append((cbuffer, sbuffer))
	return path, steps

def getProbabilityMatrix(complexes, simples, complex_ps, simple_ps, sent_similarities, sent_indexes):
	csents = []
	ssents = []
	for c in complexes:
		for s in complex_ps[c]:
			csents.append(s)
	for c in simples:
                for s in simple_ps[c]:
                        ssents.append(s)
	sizec = len(csents)
	sizes = len(ssents)
	maxsize = np.max([sizec, sizes])
	result = np.zeros((maxsize+1, maxsize+1))
	for i in range(sizec, maxsize+1):
		for j in range(0, maxsize+1):
			result[i][j] = 99999
	for j in range(sizes, maxsize+1):
		for i in range(0, maxsize+1):
			result[i][j] = 99999
	for i, cs in enumerate(csents):
		for j, ss in enumerate(ssents):
			result[i][j] = sent_similarities[sent_indexes[cs]][sent_indexes[ss]]
	text = ''
	for csent in csents:
		text += csent + '\n'
	text += '|\n'
	for ssent in ssents:
		text += ssent + '\n'
	return result, csents, ssents, text.strip()

def getAlignmentMaps(path):
	cmap = {}
	smap = {}
	for node in path:
		cmap[node[0]] = []
		smap[node[1]] = []
	for node in path:
		cmap[node[0]].append(node[1])
		smap[node[1]].append(node[0])
#	complexes = list(cmap.keys())
	simples = list(smap.keys())
	for simple in simples:
		if len(smap[simple])==1:
			if simple in cmap[smap[simple][0]]:
				del smap[simple]
#	newset = set([])
#	for c in cmap:
#		for v in cmap[c]:
#			newset.add((c,v))
#	for s in smap:
#		for v in smap[s]:
#			newset.add((v,s))
#	inter = newset.intersection(set(path))
#	if len(inter)!=len(path):
#		print('Problem!')
	return cmap, smap

def getLargeNgramMatches(complex_ps, simple_ps):
	cmap = []
	for c in complex_ps:
		cvec = []
		for s in c:
			cvec.extend(ngrams(s.split(' '), 7))
		cmap.append(set(cvec))
	smap = []
        for c in simple_ps:
                svec = []
                for s in c:
                        svec.extend(ngrams(s.split(' '), 7))
                smap.append(set(svec))

	alignments = set([])
	for i, cvec in enumerate(cmap):
		for j, svec in enumerate(smap):
			inter = cvec.intersection(svec)
			if len(inter)>0:
				alignments.add((i,j))
	return alignments

def getIdenticalMatches(complex_map, simple_map):
	csents = set(complex_map.keys())
	ssents = set(simple_map.keys())
	common = csents.intersection(ssents)
	palignments = set([])
	if len(common)>0:
		for c in common:
			complexes = complex_map[c]
			simples = simple_map[c]
			for complex in complexes:
				for simple in simples:
					palignments.add((complex, simple))

	return palignments

def getNextAlignment(currXY, searchvocab, similarities):
	cands = {}
	precvocab = set([(1,1),(1,0),(0,1)])
	auxvocab = set([(1,2),(2,1)])
	for pos in searchvocab:
		candXY = (currXY[0]+pos[0], currXY[1]+pos[1])
		sim = -99999
		try:
			sim = similarities[candXY[0]][candXY[1]]
		except Exception:
			pass
		cands[candXY] = sim
	winners = sorted(cands.keys(), key=cands.__getitem__, reverse=True)

	nearest = [cands[(currXY[0]+pos[0], currXY[1]+pos[1])] for pos in precvocab]
        if np.max(nearest)>=0.3:
                auxes = [(currXY[0]+pos[0], currXY[1]+pos[1]) for pos in auxvocab]
                for aux in auxes:
                        winners.remove(aux)
                return winners[0], cands[winners[0]]
        else:
                all = [cands[c] for c in cands]
                #In case none of the scenarios are good enough:
                if np.max(all)<0.3:
                        finalNextXY = getNextSynchronizer(currXY, similarities)
			return finalNextXY, similarities[finalNextXY[0]][finalNextXY[1]]
                else:
                        return winners[0], cands[winners[0]]

def getNextSynchronizer(currXY, similarities):
	cands = {}
	orig = currXY
	last = [len(similarities), len(similarities[0])]
	for i in range(orig[0], last[0]):
		for j in range(orig[1], last[1]):
			if i!=orig[0] and j!=orig[1] and similarities[i][j]>=0.3:
				cands[(i, j)] = (i-orig[0])+(j-orig[1])
	if len(cands)>0:
		closest = sorted(cands.keys(), key=cands.__getitem__)
		return closest[0]
	else:
		return (last[0]-1, last[1]-1)

def getOriginalParagraph(paragraphs, map):
	final = ''
	for paragraph in paragraphs:
		for sentence in map[paragraph]:
			final += sentence + '\n'
	return final.strip()

def getParagraphMap(file):
	f = open(file)
	paragraphs = []
	newparag = []
	line = f.readline().strip()
	while len(line)>0:
		newparag.append(line)
		line = f.readline().strip()
		while len(line)>0:
			newparag.append(line)
			line = f.readline().strip()
		if not (len(newparag)==1 and newparag[0].startswith('# #')):
			paragraphs.append(newparag)
#		else:
#			print('Culprit: ' + str(newparag))
		newparag = []
		line = f.readline().strip()
	f.close()
	map = {}
	for i, p in enumerate(paragraphs):
		for sentence in p:
			if sentence not in map:
				map[sentence] = set([])
			map[sentence].add(i)
	return map, paragraphs

files = os.listdir('../../corpora/truecased_corpus/')

map = {}
for file in files:
	if '.es.' not in file:
		named = file.strip().split('.')
		name = named[0]
		level = int(named[2])
		if name not in map:
			map[name] = []
		map[name].append(level)

for name in map:
	print(str(name))
	levels = sorted(map[name])
#	print levels
	for i in range(0, levels[len(levels)-1]):
		for w in range(i+1, levels[len(levels)-1]+1):
#			print('For ' + str(i) + ' to ' + str(k))
			#Get sentence-to-paragraphIDS and paragraph lists:
			complex_map, complex_ps = getParagraphMap('../../corpora/truecased_corpus/'+name+'.en.'+str(i)+'.txt')
			simple_map, simple_ps = getParagraphMap('../../corpora/truecased_corpus/'+name+'.en.'+str(w)+'.txt')
	
			#Get size of paragraphs in each file:
			sizec = len(complex_ps)
			sizes = len(simple_ps)
	
			#Create data structure for TFIDF model:
			documents = []
			csents = set(complex_map.keys())
			ssents = set(simple_map.keys())
			allsents = list(csents.union(ssents))
			sent_indexes = {}
			for j, s in enumerate(allsents):
				documents.append(s.strip())
				sent_indexes[s] = j
	
			#Filter stop words:
			stoplist = set([line.strip() for line in open('../../corpora/stop_words.txt')])
	
			#Get TFIDF model and similarity querying framework:
			texts = [[word for word in document.split() if word not in stoplist] for document in documents]
			dictionary = gensim.corpora.Dictionary(texts)
			corpus = [dictionary.doc2bow(text) for text in texts]
			tfidf = gensim.models.TfidfModel(corpus)
			index = gensim.similarities.MatrixSimilarity(tfidf[corpus])
	
			#Create TFIDF similarity matrix:
			sent_similarities = []
			for j in range(0, len(allsents)):
				sims = index[tfidf[corpus[j]]]
				sent_similarities.append(sims)
			similarities = list(np.zeros((len(complex_ps), len(simple_ps))))
			for j, cp in enumerate(complex_ps):
				for k, sp in enumerate(simple_ps):
					values = []
					for cps in cp:
						for sps in sp:
							values.append(sent_similarities[sent_indexes[cps]][sent_indexes[sps]])
					similarities[j][k] = np.max(values)
	
			#Calculate alignment path:
			path = [(0, 0)]
			currXY = (0, 0)
			searchvocab = [(1,1),(1,0),(0,1),(2,1),(1,2)]
			while currXY[0]<sizec-1 or currXY[1]<sizes-1:
				nextXY, nextXYsim = getNextAlignment(currXY, searchvocab, similarities)
				if nextXY[0]==sizec-1 and nextXY[1]==sizes-1:
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

			o = open('../../corpora/paragraphnotransitive_aligned_corpus/'+name+'.en.'+str(i)+'.'+str(w)+'.txt', 'w')
			for node in compact_path:
				c = getOriginalParagraph(node[0], complex_ps)
				s = getOriginalParagraph(node[1], simple_ps)
				o.write(c+'\n|\n')
				o.write(s+'\n\n')
			o.close()
