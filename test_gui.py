from massalign.core import *

#Get files to align:
file1 = './sample_data/test_document_complex.txt'
file2 = './sample_data/test_document_simple.txt'

#Train model over them:
model = TFIDFModel([file1, file2], './sample_data/stop_words.txt')

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

#Display paragraph alignments:
m.visualizeParagraphAlignments(p1s, p2s, alignments)
m.visualizeListOfParagraphAlignments([p1s, p1s], [p2s, p1s], [alignments, alignments])

#Align sentences in each pair of aligned paragraphs:
p1l = []
p2l = []
alignmentsl = []
for a in aligned_paragraphs:
	p1 = a[0]
	p2 = a[1]
	alignments, aligned_sentences = m.getSentenceAlignments(p1, p2, sentence_aligner)
	p1l.append(p1)
	p2l.append(p2)
	alignmentsl.append(alignments)

#Display the list of sentence alignments produced:
m.visualizeSentenceAlignments(p1l[0], p2l[0], alignmentsl[0])
m.visualizeListOfSentenceAlignments(p1l, p2l, alignmentsl)

#Create a sentence pair annotation example
src = "Hershey left no heirs when he died in 1945 , giving most of his fortune to charity ."
ref = "Hershey died in 1945 and gave most of his fortune to charity ."
word_aligns = "18-13 12-7 13-8 14-9 15-10 16-11 17-12 7-2 8-3 9-4 1-1 11-6"
src_parse = "(ROOT (S (NP (NNP Hershey)) (VP (VBD left) (NP (DT no) (NNS heirs)) (SBAR (WHADVP (WRB when)) (S (NP (PRP he)) (VP (VBD died) (PP (IN in) (NP (CD 1945))) (, ,) (S (VP (VBG giving) (NP (NP (JJS most)) (PP (IN of) (NP (PRP$ his) (NN fortune)))) (PP (TO to) (NP (NN charity))))))))) (. .)))"
ref_parse = "(ROOT (S (NP (NNP Hershey)) (VP (VP (VBD died) (PP (IN in) (NP (CD 1945)))) (CC and) (VP (VBD gave) (NP (NP (JJS most)) (PP (IN of) (NP (PRP$ his) (NN fortune)))) (PP (TO to) (NP (NN charity))))) (. .)))"

#Annotate the pair:
annotator = SentenceAnnotator()
annotations = m.getSentenceAnnotations(src.split(' '), ref.split(' '), annotator, aligns=word_aligns, src_parse=src_parse, ref_parse=ref_parse)

#Display annotations:
m.visualizeSentenceAnnotations(src, ref, word_aligns, annotations)
