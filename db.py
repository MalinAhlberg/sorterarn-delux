import logging
import os
import time
import sqlite3
import xml.etree.ElementTree as etree
from peewee import *

import pdb


inspect_key = "\t"
xml_key = "x"

# SQLite database using WAL journal mode and 64MB cache.
init_sqlite_db = SqliteDatabase('test.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})


class BaseModel(Model):
    """A base model that will use our Sqlite database."""
    class Meta:
        database = init_sqlite_db

class Sentence(BaseModel):
    text = TextField()
    xml = BlobField()
    corpus = CharField()
    congruent = BooleanField()
    tense_type = CharField()
    compound_tense = BooleanField()


tense_types = ['evaluative', 'modifying', None]
corpora = ['familjeliv', 'flashback', None]


def init_db():
    for table in [Sentence]:
        if not table.table_exists():
            logging.info(f"Creating table '{table.__name__}'")
            table.create_table()


def test():
    sent = Sentence(text='hej\tsa\tapan bob',
                    xml='<sent><w>hej<\w><\sent>',
                    corpus='familjeliv',
                    congruent=True,
                    tense_type=None,
                    compound_tense=False)
    sent.save()


# Import data from .txt + .xml
def import_data(txt, corpus, tensetype=None, xml=None):

    root = etree.parse(xml).getroot()
    sents = list(root.iterfind('.//sentence'))
    num = 0
    for line in open(txt):
        sent = Sentence(text=line,
                        xml=etree.tostring(sents[num]),
                        corpus=corpus,
                        congruent=False,
                        tense_type=tensetype,
                        compound_tense=False)
        sent.save()
        num += 1


# Search by tags
def find_by_corpus(corpus):
    selection = Sentence().select().where(Sentence.corpus == corpus)
    print(f'Found {selection.count()} sentences')
    return selection


def find_by_query(query):
    # 'select * from sentence where congruent = 1'
    q = 'select * from sentence where %s;' % query
    selection = Sentence.raw(q)
    print(f'found {len(selection)}')
    return selection


def get_by_id(sentences):
    """Get new version of each sentence from db."""
    ids = [s.id for s in sentences]
    return Sentence().select().where(Sentence.id << ids)


# change tags
def change_tags(selection, field, minutes=60):
    now = time.time()
    inspected, updated = 0, 0
    paused = False
    for sent in get_by_id(selection):
        newval = inspect_update(sent, field)
        #pdb.set_trace()
        if newval and newval != get_field(sent, field):
            Sentence.update({get_field_id(field):newval}).where(Sentence.id == sent.id).execute()
            updated += 1
        inspected += 1
        if check_time(minutes, now):
            paused = True
            break
    if not paused:
        print("No more sentences to sort! You are amazing!")
    print(f'Updated {updated} out of {inspected} sentences')


def shortcuts(field):
    values = [get_field(val, field) for val in Sentence.select(get_field_id(field)).distinct()]
    return dict(zip(range(len(values)), values))


def print_shortcuts(shortcuts):
    print(f"Shortcuts:")
    for key, val in shortcuts.items():
        print(f"{key}: {val}")


def inspect_update(sentence, field):
    # TODO add sorterarn features
    # more inspection (xml, values etc)
    # update more than one field
    os.system("clear")
    shorts = shortcuts(field)
    print(sentence.text)
    print(f"{field}: {get_field(sentence, field)}")
    print_shortcuts(shorts)
    print(f"{field}: ", end="")
    newval = input()
    if newval == inspect_key:
        inspect(sentence)
        inspect_update(sentence, field)
    try:
        return shorts[int(newval.strip())]
    except:
        return newval.strip()


def inspect(sentence):
    os.system("clear")
    print(sentence.id)
    print(sentence.text)
    fields = columns().items()
    for num, (field, val) in enumerate(fields):
        if field not in ['xml', 'text', 'id']:
            print(f"{num}. {field}: {val(sentence)}")
    action = input().strip()
    if action == xml_key:
        show_xml(sentence)
        inspect(sentence)
    if action.isdigit():
        field, val = list(fields)[int(action)]
        print(f"{field}: ", end="")
        newval = input().strip()
        if newval and newval != val:
            Sentence.update({get_field_id(field):newval}).where(Sentence.id == sentence.id).execute()
            return True
    return False


def show_xml(sentence):
    os.system("clear")
    print(sentence.xml)
    input()


def columns():
    cols = {"id": lambda x: x.id,
            "text": lambda x: x.text,
            "xml": lambda x: x.xml,
            "corpus": lambda x: x.corpus,
            "congruent": lambda x: x.congruent,
            "tense_type": lambda x: x.tense_type,
            "compound_tense": lambda x: x.compound_tense}
    return cols



def get_field(sentence, field):
    return columns()[field](sentence)


def get_field_id(field):
    # TODO
    sent = {"id": Sentence.id,
            "text": Sentence.text,
            "xml": Sentence.xml,
            "corpus": Sentence.corpus,
            "congruent": Sentence.congruent,
            "tense_type": Sentence.tense_type,
            "compound_tense": Sentence.compound_tense}
    return sent[field]



def check_time(minutes, start_time):
    now = time.time()
    time_lapsed = (now-start_time)/60.0
    if minutes > time_lapsed:
        return False
    else:
        print("Take a break baby!")
        return True

# combine with verbittarn
# combine with sorterarn
# export
