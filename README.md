## Importing data

First time set up: 

```
db.init_db()
```

Import from text file. Optional: xml, corpus and all other fields.

```
import db
db.import_data('../evaluative.txt', xml='../evaluative.xml', tense_type='evaluative', corpus='familjelivet')
```

## Selecting sentences

### By query
You can select a set of sentences by their values:
```
>>> sel = db.find_by_query('corpus = "familjeliv"')
found 491

>>> sel = db.find_by_query('corpus = "familjeliv" and congruent = True')
found 2
```

### By xml structure
You can use verbhittarn features to select sentences. The head word is the focused verb,
and you can put restrictions on one of its child word:
```
>>> matching, non_matching = db.select_by_xml(sel, {'msd': 'VB.SUP.AKT', 'deprel': 'VG'})
Found 2 matching sentences
```


## Labeling and inspecting

To inspect a selection of sentences, run
```
db.inspect(matching)
```
Press enter to see the next sentence. Press tab + enter to update the sentence.



Label a selection of sentences (update one of the fields of each sentences) by using
the function `label()`.
```
db.label(sel, 'congruent', minutes=60)
```

Tab (and then enter) will give more information about the current sentence.

To resume the previous labeling session, use:
```
resume(field="", minutes=60)
```

## Exporting
To export a selection of sentences to a file, run
```
db.export(matching, 'selection.txt')
```
or
```
db.export(matching, 'selection.txt', 'selection.xml')
```
