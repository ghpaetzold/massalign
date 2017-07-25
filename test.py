from massalign.core import *

file1 = '../newsela/corpora/truecased_corpus/orioles-alvarez.en.0.txt'
file2 = '../newsela/corpora/truecased_corpus/orioles-alvarez.en.1.txt'

model = TFIDFModel(['../newsela/corpora/truecased_corpus/orioles-alvarez.en.0.txt', '../newsela/corpora/truecased_corpus/orioles-alvarez.en.1.txt'], '../newsela/corpora/stop_words.txt')

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
	print path