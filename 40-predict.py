
import lightgbm as lgb
import pickle
import dill
import MeCab

import http.server
import socketserver
import json
lgb_clf    = pickle.load(open('vars/lgb_clf.pkl', 'rb')) 
vectorizer = dill.load(open('vars/vectorizer.dill', 'rb'))
ready_df, tfvocab = pickle.load(open('vars/tfidf.saprse', 'rb')) 
m = MeCab.Tagger('-Owakati')
def get_col(col_name): return lambda x: x[col_name]

class Handler(http.server.SimpleHTTPRequestHandler):
  def _set_response(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
 
  def do_GET(self):
    print("Client requested:", self.command, self.path )
    self.wfile.write(bytes("Hello Machine Learning !",'utf8'))
  
  def do_POST(self):
    content_length = int(self.headers['Content-Length'])
    data = self.rfile.read(content_length) 
    data = json.loads( data.decode() )
    wa   = m.parse( data['texts'] ).strip()
    sp   = vectorizer.transform([{'texts': wa}])
    yp   = lgb_clf.predict(sp).tolist()[-1]
    print( data )
    print( yp )
    self._set_response()
    # write here what you want to do
    self.wfile.write(bytes( json.dumps( {'score':yp}, ensure_ascii=False),'utf8'))

'''
wa = m.parse( '一夜一代に夢見頃' ).strip()
sp = vectorizer.transform([{'texts': wa}])

yp = lgb_clf.predict(sp)
print(yp)
'''

httpd = socketserver.TCPServer(('0.0.0.0', 4567), Handler)
httpd.serve_forever()
