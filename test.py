from massalign.core import *
import os

files = sorted(os.listdir('../newsela/corpora/truecased_corpus/'))

for i in range(0, len(files)-1):
	for j in range(i+1, len(files)):
		file1 = files[i].split('.')
		file2 = files[j].split('.')
		if file1[0]==file2[0] and int(file1[2])<int(file2[2]):
			file1 = '../newsela/corpora/truecased_corpus/'+files[i]
			file2 = '../newsela/corpora/truecased_corpus/'+files[j]

			print files[i], files[j]
		
			model = TFIDFModel([file1, file2], '../newsela/corpora/stop_words.txt')

			paragraph_aligner = VicinityDrivenParagraphAligner(similarity_model=model, acceptable_similarity=0.3)

			sentence_aligner = VicinityDrivenSentenceAligner(similarity_model=model, acceptable_similarity=0.2, similarity_slack=0.05)

			m = MASSAligner()
			p1s = m.getParagraphsFromDocument(file1)
			p2s = m.getParagraphsFromDocument(file2)
			alignments, aligned_paragraphs = m.getParagraphAlignments(p1s, p2s, paragraph_aligner) 

			for a in aligned_paragraphs:
				p1 = a[0]
				p2 = a[1]
				path = sentence_aligner.alignSentencesFromParagraphs(p1, p2)
