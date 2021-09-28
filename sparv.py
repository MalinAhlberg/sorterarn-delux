import db

import xml.etree.ElementTree as ET
import re
import urllib.parse
import urllib.request


settings =  {      "textmode": "plain",
    "word_segmenter": "default_tokenizer",
    "sentence_segmentation": {
        "sentence_chunk": "paragraph",
        "sentence_segmenter": "blanklines"
    },
    "paragraph_segmentation": {
        "paragraph_segmenter": "blanklines"
    },
    "positional_attributes": {
        "lexical_attributes": [
            "pos",
            "msd",
            "lemma",
            "lex",
            "sense"
        ],
        "compound_attributes": [],
        "dependency_attributes": [
            "ref",
            "dephead",
            "deprel"
        ],
        "sentiment": []
    },
    "named_entity_recognition": [],
    "text_attributes": {
        "readability_metrics": []
    }
}

def annotate(sents):
    """Get annotations for a sentence."""

    urlsettings = str(settings).replace("'",'"').replace(' ','')
    data = {'text': '\n\n'.join([s.text for s in sents])}
    data = urllib.parse.urlencode(data).encode('utf-8')
    url = f'https://ws.spraakbanken.gu.se/ws/sparv/v2/?settings={urlsettings}'
    req =urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        ans = response.read()
    tree = ET.fromstring(ans)
    xml = [ET.tostring(x) for x in tree.findall('.//sentence')]
    if len(xml) != len(sents):
        print(f"Something went wrong! Sparv miscounted sentences. Disgarding id {[s.id for s in sents]}")
    for sxml, sentence in zip(xml, sents):
        db.Sentence.update({db.Sentence.xml: sxml}).where(
            db.Sentence.id == sentence.id
        ).execute()
    return xml


def annotate_selection(selection):
    done = 0
    print_progressbar(done, len(selection))
    for sents in chunk(selection, 500):
        annotate(sents)
        done += len(sents)
        print_progressbar(done, len(selection))


# Print iterations progress
def print_progressbar(iteration, total, decimals=1, length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = '_' * filledLength + '-' * (length - filledLength)
    print(f'\r |{bar}| {percent}% ', end="\r")
    # Print New Line on Complete
    if iteration == total:
        print()


def chunk(list, size):
    for i in range(0, len(list), size):
        yield list[i: i+size]
