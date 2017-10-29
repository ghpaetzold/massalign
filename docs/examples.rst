.. highlightlang:: python

Examples
==================

Here you will find examples that teach you how to use MASSAlign.

Extracting and Visualizing Paragraph Alignments
------------------------------------------------

.. code-block:: python

	from massalign.core import *

	#Get files to align:
	file1 = 'https://ghpaetzold.github.io/massalign_data/complex_document.txt'
	file2 = 'https://ghpaetzold.github.io/massalign_data/simple_document.txt'

	#Train model over them:
	model = TFIDFModel([file1, file2], 'https://ghpaetzold.github.io/massalign_data/stop_words.txt')

	#Get paragraph aligner:
	paragraph_aligner = VicinityDrivenParagraphAligner(similarity_model=model, acceptable_similarity=0.3)

	#Get MASSA aligner:
	m = MASSAligner()

	#Get paragraphs from the document:
	p1s = m.getParagraphsFromDocument(file1)
	p2s = m.getParagraphsFromDocument(file2)

	#Align paragraphs:
	alignments, aligned_paragraphs = m.getParagraphAlignments(p1s, p2s, paragraph_aligner)
	
	#Display paragraph alignments:
	m.visualizeParagraphAlignments(p1s, p2s, alignments)
	m.visualizeListOfParagraphAlignments([p1s, p1s], [p2s, p2s], [alignments, alignments])

Extracting and Visualizing Sentence Alignments
-----------------------------------------------

.. code-block:: python

	from massalign.core import *

	#Get files to align:
	file1 = 'https://ghpaetzold.github.io/massalign_data/complex_document.txt'
	file2 = 'https://ghpaetzold.github.io/massalign_data/simple_document.txt'

	#Train model over them:
	model = TFIDFModel([file1, file2], 'https://ghpaetzold.github.io/massalign_data/stop_words.txt')

	#Get paragraph aligner:
	paragraph_aligner = VicinityDrivenParagraphAligner(similarity_model=model, acceptable_similarity=0.3)

	#Get sentence aligner:
	sentence_aligner = VicinityDrivenSentenceAligner(similarity_model=model, acceptable_similarity=0.2, similarity_slack=0.05)

	#Get MASSA aligner for convenience:
	m = MASSAligner()

	#Get paragraphs from the document:
	p1s = m.getParagraphsFromDocument(file1)
	p2s = m.getParagraphsFromDocument(file2)

	#Align paragraphs:
	alignments, aligned_paragraphs = m.getParagraphAlignments(p1s, p2s, paragraph_aligner)
	
	#Align sentences in each pair of aligned paragraphs:
	alignmentsl = []
	for a in aligned_paragraphs:
		p1 = a[0]
		p2 = a[1]
		alignments, aligned_sentences = m.getSentenceAlignments(p1, p2, sentence_aligner)
		
		#Display sentence alignments:
		m.visualizeSentenceAlignments(p1, p2, alignments)
		m.visualizeListOfSentenceAlignments([p1, p1], [p2, p2], [alignments, alignments])

Extracting and Visualizing Word-Level Annotations for Sentences
----------------------------------------------------------------

.. code-block:: python

	from massalign.core import *
	from massalign.util import *

	#Get MASSA aligner for convenience:
	m = MASSAligner()

	#Create a sentence pair annotation example
	reader = FileReader('https://ghpaetzold.github.io/massalign_data/annotator_data.txt')
	data = reader.getRawText().split('\n')
	src = data[0].strip()
	ref = data[1].strip()
	word_aligns = data[2].strip()
	src_parse = data[3].strip()
	ref_parse = data[4].strip()

	#Annotate the pair:
	annotator = SentenceAnnotator()
	annotations = m.getSentenceAnnotations(src.split(' '), ref.split(' '), annotator, aligns=word_aligns, src_parse=src_parse, ref_parse=ref_parse)

	#Display annotations:
	m.visualizeSentenceAnnotations(src, ref, word_aligns, annotations)