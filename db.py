import logging
import os
import re
import time
import lxml.etree as etree

from peewee import *

from model import *

import pdb


def init_db():
    """Check if the tables exist, otherwise create them."""
    for table in [Sentence, TodoList]:
        if not table.table_exists():
            logging.info(f"Creating table '{table.__name__}'")
            table.create_table()


def import_data(txt, **kwargs):
    """
    Import data from a txt file.

    Optionally add metadata (corpus, xml file or other field values.)
    """

    if "xml" in kwargs:
        root = etree.parse(kwargs["xml"]).getroot()
        sents = list(root.iterfind(".//sentence"))

    def get_sentence_xml(num):
        if "xml" in kwargs:
            return etree.tostring(sents[num])
        return "<xml/>"

    num = 0
    print(f"Read {txt}")
    for line in open(txt):
        xml = get_sentence_xml(num)
        verb = get_verb(line)
        sent = parse_sentence(line, num, parsed_xml=xml, verb=verb, **kwargs)
        sent.save()
        num += 1
    print(f"Imported {num} sentences\n")


def get_verb(sentence):
    m = re.search('\t(.*)\t', sentence)
    if m is None:
        m = re.search('^(.*)\t', sentence)
    return m.group(1)
    
        

def find_by_corpus(corpus):
    """Find all sentences in a corpus."""
    selection = Sentence().select().where(Sentence.corpus == corpus)
    print(f"Found {selection.count()} sentences")
    return selection


def find_by_query(query, create_todo=True):
    """
    Find all sentences by giving an sql where clause.

    Example: `find_by_query("corpus = 'familjeliv'")`
    """
    q = "select * from sentence where %s;" % query
    selection = Sentence.raw(q)
    print(f"found {len(selection)}")
    if create_todo:
        print(f"Creating todolist...")
        make_todolist(selection)
        print(f"Todolist created.")
    return selection


def make_todolist(sentences):
    TodoList.delete().execute()
    for sent in sentences:
        TodoList(sent=sent.id, checked=False).save()

def check_todolist():
    todos = TodoList.select().where(TodoList.checked == 0).count()
    print(f"You have {todos} sentences to do.")
    return todos


def mark_as_done(sentence):
    TodoList.update(checked=True).where(TodoList.sent==sentence.id).execute()


def resume(field="", minutes=60):
    todos = TodoList.select().where(TodoList.checked == 0)
    label((t.sent for t in todos), field, minutes)


def get_by_id(sentences):
    """Get new version of each sentence from db."""
    step = 999
    for x in range(0, len(sentences), step):
        ids = [s.id for s in sentences[x:x+step]]
        yield Sentence().select().where(Sentence.id << ids)


def inspect(selection):
    label(selection, "", 1000)


def label(selection, field, minutes=60):
    """Go through selected sentences and show them, possible update them."""
    now = time.time()
    inspected, updated = 0, 0
    paused = False
    if isinstance(field, str):
        fields = [field]
    else:
        fields = field
    last = None
    for sent in selection:
        try:
            inspected += 1
            sent_updated = False
            for field in fields:
                sent_updated = inspect_update(sent, field, last=last) or sent_updated
            updated += int(sent_updated)
            last = sent
        except KeyboardInterrupt:
            print("\nInterrupted.")
            paused = True
            break
        except Exception as e:
            log(f"Error in sentence {sent.id}, {sent.text}:")
            log(e)
            print(f"That did not work. Press any key to continue.")
            input()
        if check_time(minutes, now):
            paused = True
            break
    #if not paused and field:
    if not check_todolist():
        print("No more sentences to sort! You are amazing!")
    print(f"Updated {updated} out of {inspected} inspected sentences")


def shortcuts(column):
    """Create digit shortcuts for the values of a column in the Sentence table."""

    def sorter(val):
        if val is None:
            # put this very late, hopefully last...
            return chr(10000)
        return str(val)

    values = [
        get_field(val, column)
        for val in Sentence.select(get_field_id(column)).distinct()
    ]
    values.sort(key=sorter)
    return dict(zip(range(len(values)), values))


def print_shortcuts(shortcuts):
    """Print column shortcuts."""
    print(f"Shortcuts:")
    data = list(shortcuts.items())
    chunks = [data[x:x+3] for x in range(0, len(data), 3)]
    for row in chunks:
        for key, val in row:
            #print("".join(f"{key}: {val}".ljust(col_width)), end='\t')
            print(f"{key}: {val}",end='\t')
        print()        
    print('\n')


def inspect_update(sentence, field, last=None, updated=False):
    """Inspect a sentence, focusing on the column `field`, optionally update it."""
    newval = print_sentence(sentence, field)
    if newval == BACK:
        if last:
            updated = inspect_update(last, field)
            newval = print_sentence(sentence, field)
        else:
            print("No preceeding sentence.")
            input()
            return inspect_update(sentence, field, updated=updated, last=last)
    mark_as_done(sentence)
    if newval == INSPECT_KEY:
        updated = deep_inspect(sentence)
        return inspect_update(sentence, field, updated=updated, last=last)

    else:
        if newval.strip().isdigit():
            # try to use value as a shortcut
            try:
                newval = shorts[int(newval.strip())]
            except (ValueError, KeyError) as err:
                log(f"Invalid option {err}")
                print(f"That did not work. Press any key to try again.")
                input()
                return inspect_update(sentence, field, last=last, updated=updated)

        if newval != "" and newval != get_field(sentence, field):
            Sentence.update({get_field_id(field): convert(newval)}).where(
                Sentence.id == sentence.id
            ).execute()
            log_update(
                f"update({{ {get_field_id(field).name}: {convert(newval)} }}).where(Sentence.id == {sentence.id})"
            )
            return True
    return updated


def print_sentence(sentence, field):
    os.system("clear")
    shorts = {}
    # get a new version of the sentence
    sentence = Sentence().get_by_id(sentence.id)
    print(sentence.id)
    print(sentence.text)
    if field:
        shorts = shortcuts(field)
        print(f"{field}: {get_field(sentence, field)}")
        print_shortcuts(shorts)
        print(f"{field}: ", end="")
    return input()


def deep_inspect(sentence, msg="", updated=False):
    """Make a deeper inspection of a sentence, and optionally update any column."""
    os.system("clear")
    # get a new version of the sentence
    sentence = Sentence().get(Sentence.id == sentence.id)
    print(msg, end=" ")
    print(sentence.id)
    print(sentence.text)
    fields = show_columns()
    for num, field in enumerate(fields):
        # Dont alllow updates of xml, text or id
        if field not in ["xml", "text", "id", "verb"]:
            print(f"{num}. {field}: {get_field(sentence, field)}")
    action = input().strip()
    if action == XML_KEY:
        show_xml(sentence)
        return deep_inspect(sentence)
    if action.isdigit():
        if int(action) >= len(fields):
            return deep_inspect(sentence, "Invalid field, try again.")
        field, val = list(fields)[int(action)]
        print(f"{field}: ", end="")
        newval = input().strip()
        if newval and newval != val:
            Sentence.update({get_field_id(field):convert(newval)}).where(
                Sentence.id == sentence.id
            ).execute()
            log_update(
                f"update({{ {get_field_id(field).name}: {convert(newval)} }}).where(Sentence.id == {sentence.id})"
            )
            return deep_inspect(sentence, msg="Updated!", updated=True)
    return True


def show_xml(sentence):
    """Pretty print the xml of a sentence."""
    os.system("clear")
    print(pretty_xml(sentence))
    input()


def pretty_xml(sentence):
    """Create pretty string of the xml of a sentence."""
    return etree.tostring(
        etree.fromstring(sentence.xml), encoding="unicode", pretty_print=True
    )


def convert(value):
    """Override peewee's (?) conversion of "False" to True."""
    if isinstance(value, str) and value.lower() == "false":
        return False
    if isinstance(value, str) and value.strip().lower() in ["none", "null"]:
        return None
    return value


def export(sentences, filename, xmlfile=""):
    """
    Export a selection of sentences to file.

    Print the text represention to a given file,
    possibly also print the xml representation.
    """
    fp = open(filename, "w")
    if xmlfile:
        xml_fp = open(xmlfile, "w")
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


def select_by_xml(sentences, childword):
    """
    Select all sentences where headword is the head of childword.

    headword should be the deprel head of the childword.
    childword is a dictionary giving the necessary conditions for the other word.
    """
    matches = []
    non_matches = []

    for sentence in sentences:
        pre, word = sentence.text.split("\t", 1)
        position = len(pre.split())
        sent_xml = etree.fromstring(sentence.xml)
        for head in get_matching(position, sent_xml):
            childword["dephead"] = head.attrib["ref"]
            if get_matching(childword, sent_xml):
                matches.append(sentence)
            else:
                non_matches.append(sentence)
    print(f"Found {len(matches)} matching sentences")
    return matches, non_matches


def get_matching(worddef, sent):
    """Find all words in a sentence matching the description."""
    matches = []
    num = 0
    for word in sent.iterfind(".//w"):
        if isinstance(worddef, int):
            ok = num == worddef
        else:
            ok = True
            for key, val in worddef.items():
                if key == "word":
                    if word.text != val:
                        ok = False
                elif word.attrib.get(key) != val:
                    ok = False
        if ok:
            matches.append(word)
        num += 1
    return matches


def log(err):
    """Log an error."""
    with open(ERR_FILE, "a") as fh:
        fh.write(str(err))
        fh.write("\n")


def log_update(update):
    """Log an update to the data base."""
    # note that a journal file is automatically written if the
    # data base is opened in wal-mode.
    with open(LOG_FILE, "a") as fh:
        fh.write(update)
        fh.write("\n")


def check_time(minutes, start_time):
    """Check if it's time to take a break."""
    now = time.time()
    time_lapsed = (now - start_time) / 60.0
    if minutes > time_lapsed:
        return False
    else:
        print("Take a break baby!")
        return True
        
        
def add_verbs():
    for sent in Sentence.select():
        try:
            if not sent.verb:
                verb = get_verb(sent.text)
                Sentence.update({Sentence.verb: verb}).where(Sentence.id == sent.id).execute()
            # print(f'added verb {verb} to {sent.id}')
        except:
            print(f"Did not update {sent.id}.")
            print(f"{sent.text}")

