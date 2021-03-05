import db

import xml.etree.ElementTree as ET
import re
import urllib.parse
import urllib.request


def annotate(sent):
    """Get annotations for a sentence."""

    sent = re.sub('\s+', '+', urllib.parse.quote(sent))
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
