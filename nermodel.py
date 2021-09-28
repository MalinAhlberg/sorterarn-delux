"""
Quick and dirty usage of named entity recognizition.

Usage:
First run
> import db, nermodel
> db.init_db()  # to set up the new table

Then make a selection to annotate (possibly all sentences, but better start with a few,
to make sure everything works as intended).
> sel = db.find_by_query('id < 100')
> nermodel.add_ne_info(sel)

Explore from gui or ask someone how to do it from Python.

Example query:
finding NE sections of type TIMEX in GP
  show subtype (of ne)
       congruency (of sentence)
       text (of ne)

SELECT ner.subtype, ner.text, sentence.congruent FROM ner
  JOIN sentence on sentence.id = ner.sentence_id where ner.ex = "TIMEX" and sentence.corpus = "GP"


NB! Sentences with multiple verbs will have their ne:s multiplied, one time for each verb.
"""
import lxml.etree as etree
import pdb
import model


def add_ne_info(selection):
    for sentence in selection:
        xml = etree.fromstring(sentence.xml)
        for ne_xml in xml.iterfind(".//ne"):
            text = [x for x in list(ne_xml.itertext()) if x.strip()]
            ner = model.NER(
                text=' '.join(text),
                sentence=sentence.id,
                ex=ne_xml.attrib.get('ex'),
                type=ne_xml.attrib.get('type'),
                subtype=ne_xml.attrib.get('subtype'),
            )
            ner.save()
