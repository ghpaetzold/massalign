from massalign.core import *
import os

files = sorted(os.listdir('/export/data/ghpaetzold/newsela/corpora/truecased_corpus/'))

for i in range(0, len(files)-1):
	for j in range(i+1, len(files)):
		file1 = files[i].split('.')
		file2 = files[j].split('.')
		if file1[0]==file2[0] and int(file1[2])<int(file2[2]):
			#Get files to align:
			file1 = '/export/data/ghpaetzold/newsela/corpora/truecased_corpus/'+files[i]
			file2 = '/export/data/ghpaetzold/newsela/corpora/truecased_corpus/'+files[j]

			#Train model over them:
			model = TFIDFModel([file1, file2], '/export/data/ghpaetzold/newsela/corpora/stop_words.txt')

			#Get paragraph aligner:
			paragraph_aligner = VicinityDrivenParagraphAligner(similarity_model=model, acceptable_similarity=0.3)

			#Get sentence aligner:
			sentence_aligner = VicinityDrivenSentenceAligner(similarity_model=model, acceptable_similarity=0.2, similarity_slack=0.05)

			#Get MASSA aligner:
			m = MASSAligner()

			#Get paragraphs from the document:
			p1s = m.getParagraphsFromDocument(file1)
			p2s = m.getParagraphsFromDocument(file2)

			#Align paragraphs:
			alignments, aligned_paragraphs = m.getParagraphAlignments(p1s, p2s, paragraph_aligner) 

			#Align sentences in each pair of aligned paragraphs:
			for a in aligned_paragraphs:
				p1 = a[0]
				p2 = a[1]
				path, aligned_sentences = m.getSentenceAlignments(p1, p2, sentence_aligner)
