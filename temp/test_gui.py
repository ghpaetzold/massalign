from massalign.core import *

#Get files to align:
file1 = 'zuckerberg-internet.en.0.txt'
file2 = 'zuckerberg-internet.en.1.txt'

#Train model over them:
#model = TFIDFModel([file1, file2], '/export/data/ghpaetzold/newsela/corpora/stop_words.txt')
model = TFIDFModel([file1, file2], './stop_words.txt')

#Get paragraph aligner:
paragraph_aligner = VicinityDrivenParagraphAligner(similarity_model=model, acceptable_similarity=0.3)

#Get sentence aligner:
sentence_aligner = VicinityDrivenSentenceAligner(similarity_model=model, acceptable_similarity=0.2, similarity_slack=0.05)

#Get MASSA aligner:
m = MASSAligner()

#Get paragraphs from the document:
p1s = m.getParagraphsFromDocument(file1)
p2s = m.getParagraphsFromDocument(file2)

#Create a GUI:
gui = BasicGUI()

#Align paragraphs:
alignments, aligned_paragraphs = m.getParagraphAlignments(p1s, p2s, paragraph_aligner)

#Display paragraph alignments:
gui.displayParagraphAlignment(p1s, p2s, alignments)

#Align sentences in each pair of aligned paragraphs:
for a in aligned_paragraphs:
	p1 = a[0]
	p2 = a[1]
	path, aligned_sentences = m.getSentenceAlignments(p1, p2, sentence_aligner)
