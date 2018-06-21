

#curl -v -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"texts":"一夜一代に夢見頃"}'  http://$1:80/api/1/users
import requests
import json
from pathlib import Path

from concurrent.futures import ProcessPoolExecutor as PPE
import time

import statistics
import random

paths = sorted([path for path in Path('../objs').glob('*') ])[:1000]


def pmap(path):
  try:
    obj = json.load( path.open() )
    texts = obj['text']
    payload = json.dumps( {'texts': texts} )
    r = requests.post("http://35.232.164.217", data=payload, timeout=10)
    print(r.text, texts)
    if random.random() < 0.05:
      print(r.text, texts)
    #print(obj)
  except Exception as ex:
    print(ex)

elapseds = []
for i in range(6):
  start = time.time()
  with PPE(max_workers=10) as exe:
    exe.map(pmap, paths)

  print(f'elapsed time {time.time() - start}')
  elapseds.append( time.time() - start )

print('statistics', statistics.mean(elapseds) )
