import base64
import json
import pickle


class Route:
    first_prop: str
    second_prop: str

route = Route()

route.first_prop = 'first'
route.second_prop = 'second'

print(json.dumps(route.__dict__))

def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary

# encoded = base64.b64encode(pickle.dumps(route))

json_str = json.dumps(route.__dict__)

encoded = base64.b64encode(json_str.encode('utf-8'))
decoded = encoded.decode('ascii')
decoded_1 = base64.b64decode(decoded)


print(decoded_1)
data = json.loads(decoded_1) # print(json.dumps(decoded_1))

print (data)
# my_str = b'{"foo": 42}' # b means its a byte string
# new_str = my_str.decode('utf-8') # Decode using the utf-8 encoding
#
# import json
# d = json.dumps(my_str)
# print(d)