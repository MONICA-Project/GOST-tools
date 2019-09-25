import requests
import checking_functions

#res = requests.get("http://localhost:8080/v1.0/Datastreams?$filter=name eq 'test-6'")
#obj = res.json()
#print(obj["value"])


res = checking_functions.get_item_by_name("http://localhost:8080/v1.0/Datastreams?$filter=name eq 'test-6'")
print(res)