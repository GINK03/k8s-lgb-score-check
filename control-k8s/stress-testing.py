

#curl -v -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"texts":"一夜一代に夢見頃"}'  http://$1:80/api/1/users
import requests
import json
from pathlib import Path

from concurrent.futures import ProcessPoolExecutor as PPE

paths = [path for path in Path('../objs').glob('*') ]

def pmap(path):
  obj = json.load( path.open() )
  texts = obj['text']
  payload = json.dumps( {'texts': texts} )
  r = requests.post("http://35.232.164.217", data=payload)
  print(r.text, texts)
  #print(obj)

with PPE(max_workers=32) as exe:
  exe.map(pmap, paths)
