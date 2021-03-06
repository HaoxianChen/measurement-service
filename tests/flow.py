import requests, json, time, ast
# targeted end-host is root node: h1
addr = "10.0.0.1"
# agent programs listen on port 8000
port = 8000

# --------------------------
# Configuration
# This is an example that monitors the global traffic
# --------------------------

def config():
  # a json message: to apply filter rules on targeted end-host
  # for the convenicence of packet generation within mininet, just filter the icmp pakcets
  data = {'type':  'config sketch', \
  'interface': 'INPUT', \
  'proto' : 'icmp'}
  url = 'http://' + addr + ':' + str(port)
  r = requests.post(url,data=data)

  # Targeted end-hosts response with the sketch id
  sketch_id = int(r.text)
  print sketch_id

  # message to configure counter on the sketch
  # flow size distribution: collect the distribution among different <src,dst> combinations
  data = {'type': 'config sketch counter',\
  'sketch_id': sketch_id,\
  'counter_key_type': 'src_dst',\
  'increment': 'bytes'}
  r = requests.post(url,data=data)

# ---------------------------
# Query Counters periodically
# ---------------------------

def query(sketch_id):
  # query heavy hitter from the counter
  data={'type': 'query heavy hitters', \
'sketch_id': sketch_id, \
'counter_key_type': 'src_dst'}
  url = 'http://' + addr + ':' + str(port)
  # targetted end-host response with the heavy hitter records in JSON message
  r = requests.post(url,data=data)
  if r.status_code == 200:
    # parse text to json message
    d = ast.literal_eval(r.text)
    print json.dumps(d,sort_keys=True,indent=4)
  else:
    print r.text
  
  # query one counter entry by key
  data={'type': 'query sketch', \
'sketch_id': sketch_id, \
'counter_key_type': 'src_dst',\
'counter_key': '10.0.0.6,10.0.0.5'}
  # targetted end-host response with the value
  # r = requests.post(url,data=data)
  # print 'h6 hits h5: ' +  r.text + 'times'

def run(funct, sketch_id):
  if funct == 'config':
    config()
  if funct == 'query':
    query(sketch_id)

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='This is SoNIC server')
  parser.add_argument('-f','--function',help='function to execute: config / query',default='query')
  parser.add_argument('-i','--sketch_id',help='sketch id',default='1')
  args = parser.parse_args()
  run(args.function, args.sketch_id)
