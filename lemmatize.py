import db
import xml.etree.ElementTree as ET
import re
import pdb

# First, create the column.
# db.Sentence.raw('ALTER TABLE sentence ADD lemma varchar;').execute()

# To search
# SELECT lemma from "sentence" where lemma like ('%|finna|%')

def add_lemma(sent):
    if re.search('\t(.*)\t', sent.text):
        pre, rest = sent.text.split('\t', 1)
        index = len(pre.split())
    else:  # verb is in first position
        index = 0
    sxml = ET.fromstring(sent.xml)
    wxml = sxml.findall(".//w")[index]
    if wxml.text.lower() == sent.verb.lower():
        sent.verb_lemma = wxml.attrib.get('lemma')
        sent.save()
    else:
        retry(sent, index, sxml, sent.verb)


def retry(sent, index, sxml, verb):
    matches = 0
    for wxml in sxml.findall(".//w")[max(0, index-5):index+5]:
        if wxml.text == verb:
            sent.verb_lemma = wxml.attrib.get('lemma')
            matches += 1
    if matches != 1:
        print(f'Problem! {sent.id}, {matches} matching words found')
    else:
        sent.save()



def add_lemmas(selection):
    for sent in selection:
        add_lemma(sent)


def add_manual(filep):
    for line in open(filep):
        m = re.match("id='(\d*)'.*='(.*)'", line)
        if not m:
            continue
        print(f'Add lemma {m.group(2)} to id {m.group(1)}')
        s = db.Sentence().get_by_id(m.group(1))
        s.verb_lemma = f'|{m.group(2)}|'
        s.save()