"""Configuration for the database and the sorter."""
from peewee import (
    Model,
    SqliteDatabase,
    TextField,
    BlobField,
    CharField,
    BooleanField,
)


INSPECT_KEY = "\t"
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
    xml = BlobField(null=True)
    corpus = CharField(null=True)
    congruent = BooleanField(null=True)
    tense_type = CharField(null=True)
    compound_tense = BooleanField(null=True)


# TODO use enums or similar to limit value sets?
tense_types = ["evaluative", "modifying", None]
corpora = ["familjeliv", "flashback", None]


# Ugly section :(
def columns():
    """List functions for all columns of a sentence."""
    # TODO
    cols = {
        "id": lambda x: x.id,
        "text": lambda x: x.text,
        "xml": lambda x: x.xml,
        "corpus": lambda x: x.corpus,
        "congruent": lambda x: x.congruent,
        "tense_type": lambda x: x.tense_type,
        "compound_tense": lambda x: x.compound_tense,
    }
    return cols


def get_field(sentence, field):
    """Get the reference to column `field` of a sentence."""
    return columns()[field](sentence)


def get_field_id(field):
    # TODO
    sent = {
        "id": Sentence.id,
        "text": Sentence.text,
        "xml": Sentence.xml,
        "corpus": Sentence.corpus,
        "congruent": Sentence.congruent,
        "tense_type": Sentence.tense_type,
        "compound_tense": Sentence.compound_tense,
    }
    return sent[field]
