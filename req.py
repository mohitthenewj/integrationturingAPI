import requests
from oddf import odasdf
from ast import literal_eval

r = requests.post("http://52.190.24.117:5000", json={'ID':'20201009-074824','FPS':'1','duration':'5','lang':'', 'container':'var'})
# print(r.status_code, r.reason)

print(odasdf(literal_eval(r.text)))

# from urllib.parse import urlencode
# from urllib.request import Request, urlopen

# url = 'http://0.0.0.0:5000/' # Set destination URL here
# post_fields = {'ID': '12345'}  # Set POST fields here

# request = Request(url, urlencode(post_fields).encode())
# json = urlopen(request).read().decode()
# print(json)
# Include fps and duration on req
