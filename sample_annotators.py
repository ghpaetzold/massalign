from massalign.annotators import SentenceAnnotator

# =============================================================================
# Annotation of a single sentence
# =============================================================================

src = "Hershey left no heirs when he died in 1945 , giving most of his fortune to charity .".split(' ')
ref = "Hershey died in 1945 and gave most of his fortune to charity .".split(' ')
word_aligns = "18-13 12-7 13-8 14-9 15-10 16-11 17-12 7-2 8-3 9-4 1-1 11-6"
src_parse = "(ROOT (S (NP (NNP Hershey)) (VP (VBD left) (NP (DT no) (NNS heirs)) (SBAR (WHADVP (WRB when)) (S (NP (PRP he)) (VP (VBD died) (PP (IN in) (NP (CD 1945))) (, ,) (S (VP (VBG giving) (NP (NP (JJS most)) (PP (IN of) (NP (PRP$ his) (NN fortune)))) (PP (TO to) (NP (NN charity))))))))) (. .)))"
ref_parse = "(ROOT (S (NP (NNP Hershey)) (VP (VP (VBD died) (PP (IN in) (NP (CD 1945)))) (CC and) (VP (VBD gave) (NP (NP (JJS most)) (PP (IN of) (NP (PRP$ his) (NN fortune)))) (PP (TO to) (NP (NN charity))))) (. .)))"

singlesent_annotator = SentenceAnnotator()
sent_annots = singlesent_annotator.annotate_sentence(src, ref, word_aligns, src_parse, ref_parse)

src_conll = singlesent_annotator.dict2conll(sent_annots['src'])
ref_conll = singlesent_annotator.dict2conll(sent_annots['ref'])

print "Annotations on the source sentence:"
print src_conll
print "Annotations on the reference sentence:"
print ref_conll


# =============================================================================
# Annotation of a file with multiple sentences
# =============================================================================

sents_path = "./sample_data/annotation_sample.parallel"
aligns_path = "./sample_data/annotation_sample.aligns"
parse_path = "./sample_data/annotation_sample.stp"

with open(sents_path) as sents_file, open(aligns_path) as aligns_file, open(parse_path) as parse_file:
    # get the annotations
    file_annotator = SentenceAnnotator()
    file_annots = file_annotator.annotate_file(sents_file, aligns_file, parse_file)

    # create an output file with the annotations in conll format
    outfile_name = sents_path.split('/')[-1] + '.simops.conll'
    with open(outfile_name + '.src', 'w') as file_annots_src, open(outfile_name + '.ref', 'w') as file_annots_ref:
        file_annotator.create_conll_files(file_annots_src, file_annots_ref, file_annots, True)

    print 'Files created.'
