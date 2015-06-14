import json
data = open("out.txt","r+")
str = data.read()
encoded_str = json.dumps(str)
decoded_data = json.loads( encoded_str )
print json.dumps(decoded_data, sort_keys=True, indent=4, separators=(',',': ')) 