
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
    if wxml.text != sent.verb:
        print(f'ajaj {wxml.text} != {sent.verb}, {sent.id}')
    sent.lemma = wxml.attrib.get('lemma')
    sent.save()
