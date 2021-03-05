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
    tense = CharField(null=True)
    congruent = BooleanField(null=True)
    inc_type = CharField(null=True)
    compound_tense = BooleanField(null=True)
    trash = BooleanField(null=True)
    undecidable = BooleanField(null=True)
    meaning = CharField(null=True)
    verb = CharField(null=True)
    


class TodoList(BaseModel):
    sent = ForeignKeyField(Sentence, backref='todo')
    checked = BooleanField(default=False)


# TODO use enums or similar to limit value sets?
inc_types = ["evaluative", "modifying", None]
corpora = ["familjeliv", "flashback", None]


def get_field(sentence, field):
    """Get the reference to column `field` of a sentence."""
    return sentence.__getattribute__(field)


# Ugly section :(
def get_field_id(field):
    # TODO
    sent = {
        "id": Sentence.id,
        "text": Sentence.text,
        "xml": Sentence.xml,
        "corpus": Sentence.corpus,
        "tense": Sentence.tense,
        "congruent": Sentence.congruent,
        "inc_type": Sentence.inc_type,
        "compound_tense": Sentence.compound_tense,
        "trash": Sentence.trash,
        "undecidable": Sentence.undecidable,
        "meaning": Sentence.meaning,
        "verb": Sentence.verb,
    }
    return sent[field]


def parse_sentence(line, num, parsed_xml, **kwargs):
    sent = Sentence(
        text=line,
        xml=parsed_xml,
        corpus=kwargs.get("corpus"),
        tense=kwargs.get("tense"),
        congruent=kwargs.get("congruent"),
        inc_type=kwargs.get("inc_type"),
        trash=kwargs.get("trash"),
        compound_tense=kwargs.get("compound_tense"),
        undecidable=kwargs.get("undecidable"),
        meaning=kwargs.get("meaning"),
        verb=kwargs.get("verb"),
        )
    return sent
