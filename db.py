import logging
import os
import time
import xml.etree.ElementTree as etree
from xml.dom.minidom import parseString

from peewee import *

from model import *

import pdb


# SQLite database using WAL journal mode and 64MB cache.
init_sqlite_db = SqliteDatabase(db_name, pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})


# TODO print all errors to file. Print all updates to file.

def init_db():
    """Check if the tables exist, otherwise create them."""
    for table in [Sentence]:
        if not table.table_exists():
            logging.info(f"Creating table '{table.__name__}'")
            table.create_table()


def import_data(txt, **kwargs):
    """
    Import data from a txt file.

    Optionally add metadata (corpus, xml file or other field values.)
    """

    if 'xml' in kwargs:
        root = etree.parse(kwargs['xml']).getroot()
        sents = list(root.iterfind('.//sentence'))
    def get_sentence_xml(num):
        if 'xml' in kwargs:
            return etree.tostring(sents[num])
        return ''

    num = 0
    for line in open(txt):
        sent = Sentence(text=line,
                        xml=get_sentence_xml(num),
                        corpus=kwargs.get('corpus'),
                        congruent=kwargs.get('congruent'),
                        tense_type=kwargs.get('tense_type'),
                        compound_tense=kwargs.get('compound_tense'))
        sent.save()
        num += 1


# Search by tags
def find_by_corpus(corpus):
    """Find all sentences in a corpus."""
    selection = Sentence().select().where(Sentence.corpus == corpus)
    print(f'Found {selection.count()} sentences')
    return selection


def find_by_query(query):
    """
    Find all sentences by giving an sql where clause.

    Example: `find_by_query("corpus = 'familjeliv'")`
    """
    q = 'select * from sentence where %s;' % query
    selection = Sentence.raw(q)
    print(f'found {len(selection)}')
    return selection


def get_by_id(sentences):
    """Get new version of each sentence from db."""
    ids = [s.id for s in sentences]
    return Sentence().select().where(Sentence.id << ids)


def inspect(selection):
    sort(selection, '', 1000)


def sort(selection, field, minutes=60):
    """Go through selected sentences and show them, possible update them."""
    now = time.time()
    inspected, updated = 0, 0
    paused = False
    for sent in get_by_id(selection):
        try:
            inspected += 1
            updated += int(inspect_update(sent, field))
        except KeyboardInterrupt:
            print("\nInterrupted.")
            paused = True
            break
        except Exception as e:
            print(e)
            log(f"Error in sentence {sent.id}, {sent.text}:")
            log(e)
            print(f"That did not work. Press any key to continue.""")
            input()
        if check_time(minutes, now):
            paused = True
            break
    if not paused and field:
        print("No more sentences to sort! You are amazing!")
    print(f'Updated {updated} out of {inspected} inspected sentences')


def shortcuts(column):
    """Create digit shortcuts for the values of a column in the Sentence table."""
    def sorter(val):
        if val is None:
            # put this very late, hopefully last...
            return chr(10000)
        return str(val)

    values = [get_field(val, column) for val in Sentence.select(get_field_id(column)).distinct()]
    values.sort(key=sorter)
    return dict(zip(range(len(values)), values))


def print_shortcuts(shortcuts):
    """Print column shortcuts."""
    print(f"Shortcuts:")
    for key, val in shortcuts.items():
        print(f"{key}: {val}")


def inspect_update(sentence, field):
    """Inspect a sentence, focusing on the column `field`, optionally update it."""
    os.system("clear")
    updated = False
    shorts = {}
    sentence = Sentence().get(Sentence.id == sentence.id)
    print(sentence.id)
    print(sentence.text)
    if field:
        shorts = shortcuts(field)
        print(f"{field}: {get_field(sentence, field)}")
        print_shortcuts(shorts)
        print(f"{field}: ", end="")
    newval = input()
    if newval == inspect_key:
        updated = deep_inspect(sentence)
        inspect_update(sentence, field)
    if newval.strip().isdigit():
        try:
            # try to use value as a shortcut...
            newval = shorts[int(newval.strip())]
        except (ValueError, KeyError) as err:
            # otherwise use it as a field name
            log(f"Invalid option {err}")
            print(f"That did not work. Press any key to try again.""")
            input()
            inspect_update(sentence, field)

    if newval != '' and newval != get_field(sentence, field):
        Sentence.update({get_field_id(field): convert(newval)}).where(Sentence.id == sentence.id).execute()
        log_update(f"update({{ {get_field_id(field).name}: {convert(newval)} }}).where(Sentence.id == {sentence.id})")
        return True
    return updated
    


def deep_inspect(sentence, msg=""):
    """Make a deeper inspection of a sentence, and optionally update any column."""
    os.system("clear")
    print(msg, end="")
    print(sentence.id)
    print(sentence.text)
    fields = columns().items()
    for num, (field, val) in enumerate(fields):
        # Dont alllow updates of xml, text or id
        if field not in ['xml', 'text', 'id']:
            print(f"{num}. {field}: {val(sentence)}")
    action = input().strip()
    if action == xml_key:
        show_xml(sentence)
        deep_inspect(sentence)
    if action.isdigit():
        if int(action) >= len(fields):
            deep_inspect(sentence, "Invalid field, try again.")
        field, val = list(fields)[int(action)]
        print(f"{field}: ", end="")
        newval = input().strip()
        if newval and newval != val:
            Sentence.update({get_field_id(field):convert(newval)}).where(Sentence.id == sentence.id).execute()
            print(f"Updated")
            return True
    return False


def show_xml(sentence):
    """Pretty print the xml of a sentence."""
    os.system("clear")
    print(pretty_xml(sentence))
    input()


def pretty_xml(sentence):
    """Create pretty string of the xml of a sentence."""
    # TODO make prettier (too many newlines)
    reparsed = parseString(sentence.xml)
    return reparsed.toprettyxml(indent="\t")


def columns():
    """List functions for all columns of a sentence."""
    # TODO?
    cols = {"id": lambda x: x.id,
            "text": lambda x: x.text,
            "xml": lambda x: x.xml,
            "corpus": lambda x: x.corpus,
            "congruent": lambda x: x.congruent,
            "tense_type": lambda x: x.tense_type,
            "compound_tense": lambda x: x.compound_tense}
    return cols



def get_field(sentence, field):
    """Get the reference to column `field` of a sentence."""
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
    """Check if it's time to take a break."""
    now = time.time()
    time_lapsed = (now-start_time)/60.0
    if minutes > time_lapsed:
        return False
    else:
        print("Take a break baby!")
        return True


def convert(value):
    """Override peewee's (?) conversion of "False" to True.""" 
    if isinstance(value, str) and value.lower() == "false":
        return False
    return value


def export(sentences, filename, xmlfile=""):
    """
    Export a selection of sentences to file.
    
    Print the text represention to a given file,
    possibly also print the xml representation.
    """
    fp = open(filename, 'w')
    if xmlfile:
        xml_fp = open(xmlfile, 'w')
        xml_fp.write("<corpus><text><paragraph>")
    num = 0
    for sentence in sentences:
        fp.write(sentence.text)
        if xmlfile:
            xml_fp.write(pretty_xml(sentence))
        num += 1
    print(f"Exported {num} sentences to file {filename}.")
    if xmlfile:
        xml_fp.write("</paragraph></text></corpus>")
        print(f"Also printed xml file {xmlfile}.")


def select_by_xml():
    # TODO combine with verbittarn
    pass


def log(err):
    with open(err_file, 'a') as fh:
        fh.write(str(err))
        fh.write('\n')


def log_update(update):
    with open(log_file, 'a') as fh:
        fh.write(update)
        fh.write('\n')
