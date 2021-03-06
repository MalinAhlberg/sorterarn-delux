import db
import model
import re


def check(logfile='.db.log'):
    """Check if the db and the log agrees on the sentence values."""
    status = create_status(logfile)
    for sentid, values in status.items():
        try:
            sent = db.Sentence().get_by_id(sentid)
        except:
            print(f'Sentenec {sentid} lost?')
        for key, val in values.items():
            curr = str(model.get_field(sent, key))
            if curr != val:
                print(f'Error? Sentence {sentid}, column {key}: {val} != {curr}')


def create_status(logfile):
    """Create a dictionary with the current status, according to the log file."""
    status = {}
    for line in open(logfile):
        pattern = 'update\({\s*(.*?):\s*(.*?)\s*}\).where\(.*==\s*(\d*)\)'
        m = re.search(pattern, line)
        if not m:
            print(f'Bad line {line}')
            continue
        field, val, sentid = m.groups()
        if sentid not in status:
            status[sentid] = {}
        status[sentid].update({field: val})
    return status
