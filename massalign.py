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
		return [], []
	
	currXY = starting_point
	cbuffer = all_complex[currXY[0]]
	final_cbuffer = all_complex[currXY[0]]
	sbuffer = all_simple[currXY[1]]
	final_sbuffer = all_simple[currXY[1]]
	while currXY[0]<len(all_complex)-1 and currXY[1]<len(all_simple)-1:
		bestNextXY, bestNextXYProb = getBestNextHypothesis(matrix, all_complex, all_simple, cbuffer, sbuffer, currXY, dictionary, tfidf, minvalue, prevslack)
		#Check to see if best is diagonal:
		if bestNextXY[0]==currXY[0]+1 and bestNextXY[1]==currXY[1]+1:
			steps.append('Found best diagonal next: ' + str(bestNextXY))
#			path.append((cbuffer, sbuffer))
			path.append((final_cbuffer, final_sbuffer))
			currXY = bestNextXY
			cbuffer = all_complex[currXY[0]]
			final_cbuffer = all_complex[currXY[0]]
			sbuffer = all_simple[currXY[1]]
			final_sbuffer = all_simple[currXY[1]]
		#Check to see if downards is best:
		elif bestNextXY[0]==currXY[0]+1 and bestNextXY[1]==currXY[1]:
			anchor = bestNextXY[0]+1
			prevsim = getSimilarity(cbuffer, sbuffer, dictionary, tfidf)
			cbuffer += ' ' + all_complex[bestNextXY[0]]
			final_cbuffer += ' ||| ' + all_complex[bestNextXY[0]]
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
						final_cbuffer += ' ||| ' + all_complex[anchor]
					else:
						if currsim<=prevsim-prevslack:
							steps.append('\tStopped because currsim: ' + str(currsim) + ', prevsim: ' + str(prevsim))
						else:
							steps.append('\tStopped because currsim: ' + str(currsim) + ', diagonal: ' + str(matrix[anchor][bestNextXY[1]+1]))
						anchor -= 1
						currsim = 0.0
#			path.append((cbuffer, sbuffer))
			path.append((final_cbuffer, final_sbuffer))
			if anchor<len(all_complex):
				currXY = findStartingPoint(matrix, all_complex, all_simple, minvalue, [anchor-1, bestNextXY[1]])
				if currXY[0]<len(all_complex) and currXY[1]<len(all_simple):
					cbuffer = all_complex[currXY[0]]
					final_cbuffer = all_complex[currXY[0]]
					sbuffer = all_simple[currXY[1]]
					final_sbuffer = all_simple[currXY[1]]
			else:
				currXY = (anchor, bestNextXY[1]+1)
		elif  bestNextXY[0]==currXY[0] and bestNextXY[1]==currXY[1]+1:
			anchor = bestNextXY[1]+1
			prevsim = getSimilarity(cbuffer, sbuffer, dictionary, tfidf)
                        sbuffer += ' ' + all_simple[bestNextXY[1]]
			final_sbuffer += ' ||| ' + all_simple[bestNextXY[1]]
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
						final_sbuffer += ' ||| ' + all_simple[anchor]
					else:
						if currsim<=prevsim-prevslack:
                                                        steps.append('\tStopped because currsim: ' + str(currsim) + ', prevsim: ' + str(prevsim))
                                                else:
                                                        steps.append('\tStopped because currsim: ' + str(currsim) + ', diagonal: ' + str(matrix[bestNextXY[0]+1][anchor]))
						anchor -= 1
						currsim = 0.0
#                        path.append((cbuffer, sbuffer))
			path.append((final_cbuffer, final_sbuffer))
                        if anchor<len(all_simple):
				currXY = findStartingPoint(matrix, all_complex, all_simple, minvalue, [bestNextXY[0], anchor-1])
				if currXY[0]<len(all_complex) and currXY[1]<len(all_simple):
	                                cbuffer = all_complex[currXY[0]]
					final_cbuffer = all_complex[currXY[0]]
	                                sbuffer = all_simple[currXY[1]]
					final_sbuffer = all_simple[currXY[1]]
			else:
				currXY = (bestNextXY[0]+1, anchor)
		else:
			steps.append('Found new starting point: ' + str(bestNextXY))
#                        path.append((cbuffer, sbuffer))
			path.append((final_cbuffer, final_sbuffer))
                        currXY = bestNextXY
			if bestNextXY[0]<len(all_complex) and bestNextXY[1]<len(all_simple):
	                        cbuffer = all_complex[currXY[0]]
				final_cbuffer = all_complex[currXY[0]]
	                        sbuffer = all_simple[currXY[1]]
				final_sbuffer = all_simple[currXY[1]]

	if currXY[0]<len(all_complex) and currXY[1]<len(all_simple) and getSimilarity(cbuffer, sbuffer, dictionary, tfidf)>minvalue:
		#In case last alignment is in the very corner:			
		if currXY[0]==len(all_complex)-1 and currXY[1]==len(all_simple)-1:
#			path.append((cbuffer, sbuffer))
			path.append((final_cbuffer, final_sbuffer))
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
						final_sbuffer += ' ||| ' + all_simple[anchor+1]
				anchor += 1
#			path.append((cbuffer, sbuffer))
			path.append((final_cbuffer, final_sbuffer))
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
						final_cbuffer += ' ||| ' + all_complex[anchor+1]
                                anchor += 1
#                        path.append((cbuffer, sbuffer))
			path.append((final_cbuffer, final_sbuffer))
	return path, steps

def getProbabilityMatrix(csents, ssents, sent_similarities, sent_indexes):
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

def getOriginalParagraph(paragraph):
	final = ''
	for sentence in paragraph:
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

def getParagraphAlignments(file):
        f = open(file)
        result = []

        line = f.readline().strip()
        while len(line)>0:
                paragc = [line]
                line = f.readline().strip()
                while line!='|':
                        paragc.append(line)
                        line = f.readline().strip()
                line = f.readline().strip()
                parags = [line]
                line = f.readline().strip()
                while len(line)>0:
                        parags.append(line)
                        line = f.readline().strip()

		result.append((paragc, parags))

                line = f.readline().strip()
        f.close()

        return result

files = os.listdir('../../corpora/paragraphnotransitive_aligned_corpus/')

map = {}
for file in files:
	if '.es.' not in file:
		named = file.strip().split('.')
		name = named[0]
		level1 = int(named[2])
		level2 = int(named[3])
		if name not in map:
			map[name] = []
		map[name].append((level1, level2))

for name in map:
	print(str(name))
	for pair in map[name]:
		#Get alignment maps:
		paragraphals = getParagraphAlignments('../../corpora/paragraphnotransitive_aligned_corpus/'+name+'.en.'+str(pair[0])+'.'+str(pair[1])+'.txt')
		csents = set([])
		ssents = set([])
		for paragraphal in paragraphals:
			csents.update(paragraphal[0])
			ssents.update(paragraphal[1])
		allsents = list(csents.union(ssents))

		if len(allsents)==1:
			allsents.append('this is a placeholder .')

		#Create data structure for TFIDF model:
		documents = []
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

#		print('Complex to simple...')
		o = open('../../corpora/sentencenotransitive_sentseparated_aligned_corpus/'+name+'.en.'+str(pair[0])+'.'+str(pair[1])+'.txt', 'w')
		for paragraphal in paragraphals:
			matrix, all_complex, all_simple, alignment_text = getProbabilityMatrix(paragraphal[0], paragraphal[1], sent_similarities, sent_indexes)
			sent_path, steps = getSentenceAlignmentPath(matrix, all_complex, all_simple, dictionary, tfidf, 0.2, 0.05)
			sent_alignments = getFinalSentenceAlignments(sent_path)
			for s0 in sent_alignments:
				o.write(s0 + '\t||||||\t' + sent_alignments[s0] + '\n')
		o.close()
