import db

import xml.etree.ElementTree as ET
import re
import urllib.parse
import urllib.request


def annotate(sent):
    """Get annotations for a sentence."""

    sent = urllib.parse.quote(sent)
    url = f'https://ws.spraakbanken.gu.se/ws/sparv/v2/?text={sent}'
    with urllib.request.urlopen(url) as response:
        ans = response.read()
    tree = ET.fromstring(ans)
    return ET.tostring(tree.find('.//paragraph'))


def add_xml(sentence):
    xml = annotate(sentence.text)
    db.Sentence.update({db.Sentence.xml: xml}).where(
        db.Sentence.id == sentence.id
    ).execute()


def annotate_selection(selection):
    done = 0
    print_progressbar(done, len(selection))
    for sent in selection:
        add_xml(sent)
        done += 1
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
