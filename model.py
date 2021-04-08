"""Configuration for the database and the sorter."""
from peewee import (
    Model,
    SqliteDatabase,
    TextField,
    BlobField,
    CharField,
    BooleanField,
    ForeignKeyField,
)


INSPECT_KEY = "\t"
BACK = "\t\t"
XML_KEY = "x"
DB_NAME = "test.db"
ERR_FILE = ".db.err"
LOG_FILE = ".db.log"


# SQLite database using WAL journal mode and 64MB cache.
init_sqlite_db = SqliteDatabase(DB_NAME, pragmas={
    "journal_mode": "wal",
    "cache_size": -1024 * 64})


class BaseModel(Model):
    """Base model."""

    class Meta:
        database = init_sqlite_db


class Sentence(BaseModel):
    """Sentence model."""

    text = TextField()
    corpus = CharField(null=True)
    tense = CharField(null=True)
    congruent = BooleanField(null=True)
    inc_type = CharField(null=True)
    compound_tense = BooleanField(null=True)
    trash = BooleanField(null=True)
    undecidable = BooleanField(null=True)
    meaning = CharField(null=True)
    verb = CharField(null=True)
    temp_meaning = CharField(null=True)
    xml = BlobField(null=True)
    


class TodoList(BaseModel):
    sent = ForeignKeyField(Sentence, backref='todo')
    checked = BooleanField(default=False)


# TODO use enums or similar to limit value sets?
inc_types = ["evaluative", "modifying", None]
corpora = ["familjeliv", "flashback", None]


def get_field(sentence, field):
    """Get the reference to column `field` of a sentence."""
    return sentence.__getattribute__(field)


def show_columns():
    """ Define the changable columns."""
    # Dont alllow updates of xml, text or id
    return [
        "corpus",
        "tense",
        "congruent",
        "inc_type",
        "compound_tense",
        "trash",
        "undecidable",
        "meaning",
        "temp_meaning",
    ]


# Ugly section :(
def get_field_id(field):
    # TODO
    sent = {
        "id": Sentence.id,
        "text": Sentence.text,
        "corpus": Sentence.corpus,
        "tense": Sentence.tense,
        "congruent": Sentence.congruent,
        "inc_type": Sentence.inc_type,
        "compound_tense": Sentence.compound_tense,
        "trash": Sentence.trash,
        "undecidable": Sentence.undecidable,
        "meaning": Sentence.meaning,
        "verb": Sentence.verb,
        "temp_meaning": Sentence.temp_meaning,
        "xml": Sentence.xml,
    }
    return sent[field]


def parse_sentence(line, num, parsed_xml, **kwargs):
    sent = Sentence(
        text=line,
        corpus=kwargs.get("corpus"),
        tense=kwargs.get("tense"),
        congruent=kwargs.get("congruent"),
        inc_type=kwargs.get("inc_type"),
        trash=kwargs.get("trash"),
        compound_tense=kwargs.get("compound_tense"),
        undecidable=kwargs.get("undecidable"),
        meaning=kwargs.get("meaning"),
        verb=kwargs.get("verb"),
        temp_meaning=kwargs.get("temp_meaning"),
        xml=parsed_xml,
        )
    return sent
