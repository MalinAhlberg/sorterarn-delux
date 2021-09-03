import db
import pdb
from sparv import annotate
from model import Sentence


def split_sentence(sentence):
    """Separate the text part of sentences, as annotated with '&&&'"""
    s_id = sentence.split()[0]
    sentence = sentence.split(maxsplit=1)[1].strip().strip('\n')
    text1, text2 = sentence.split("&&&", 1)
    # get the sentence from the db
    info = Sentence().get_by_id(s_id)
    # Create a new sentence
    newsent = Sentence(
        text=text2,
        corpus=info.corpus,
        tense=info.tense,
        congruent=info.congruent,
        inc_type=info.inc_type,
        type=info.type,
        trash=info.trash,
        compound_tense=info.compound_tense,
        undecidable=info.undecidable,
        verb=info.verb,
        temp_meaning=info.temp_meaning,
        relayed_marker=info.relayed_marker,
    )
    newsent.save()
    print("Added", newsent.id)
    # Update text of the original sentence (remove second part)
    db.Sentence.update({db.Sentence.text: text1}).where(
        db.Sentence.id == s_id
    ).execute()
    # Return the old and the new sentence
    return [info, newsent]


def split_many(filepath):
    """Split a list of sentences. Each row of the file should look like
       <id>  sentence part 1&&&sentence part 2.
    """
    updated = []
    for line in open(filepath):
        updated.extend(split_sentence(line))
    # Update the xml of both sentences
    annotate(updated)
    # Return all ids
    return [s.id for s in updated]
