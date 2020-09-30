import requests
import json

# creates a shortened link through bit.ly. Didn't find this behavior in the docs but apparently bit.ly shortens
# amazon links to amzn.to links which is better so I'm not mad about it
# (the tracking still works)
def get_short_link(link):
	r = requests.post('https://api-ssl.bitly.com/v4/shorten', data=json.dumps({
		"group_guid": "Bk9r7UIHvMn",
		"domain": "bit.ly",
		"long_url": link
	}), headers={"Authorization": "Bearer 5ac68c7e9a36736347ae4786ba3989673832d8e6",
				 "Content-Type": "application/json"})
	print(json.loads(r.text))
	return json.loads(r.text)["link"]
