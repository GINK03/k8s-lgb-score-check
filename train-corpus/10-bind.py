
from pathlib import Path

import json

import MeCab

m = MeCab.Tagger('-Owakati')

points = []
texts = []
for index, path in enumerate(Path('objs').glob('*')):
  print(index, path)
  obj = json.load(path.open())
  text = m.parse(obj['text']).strip()
  texts.append( text )
  points.append( obj['point'] )

import pandas as pd

df = pd.DataFrame({'points':points, 'texts':texts}) 

df.to_csv('eiga_score_texts.csv', index=None)

