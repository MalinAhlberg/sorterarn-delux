"""
Quick and dirty usage of named entity recognition.

Usage:
First run
> import db, nermodel
> db.init_db()  # to set up the new table¨

Then make a selection to annotate (possibly all sentences, but better start with a few,
to make sure everything works as intended).
> sel = db.find_by_query('id < 100')
> nermodel.add_ne_info(sel)

Explore from gui or ask someone how to do it from Python.

### Example queries
- inspecting the ner table:
SELECT * FROM ner LIMIT 20;


- finding NE sections of type TIMEX in GP and
  showing subtype (of ne)
          congruency (of sentence)
          text (of ne)

SELECT ner.subtype, ner.text, sentence.congruent FROM ner
  JOIN sentence on sentence.id = ner.sentence_id where ner.ex = "TIMEX" and sentence.corpus = "GP"


NB! Sentences with multiple verbs will have their ne:s multiplied, one time for each verb.
"""
import lxml.etree as etree
import datetime
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


def search_ne_info(query):
    q = "select * from sentence where %s;" % query
    selection = model.Sentence.raw(q)
    start = datetime.datetime.now()
    count, fails = 0, 0
    for sentence in selection:
        try:
            xml = etree.fromstring(sentence.xml)
            for ne_xml in xml.iterfind(".//ne"):
                count += 1
        except:
            fails += 1
    print(f'Inspected {count} nes, could not parse {fails}')
    print(f'Took {datetime.datetime.now()-start}')
