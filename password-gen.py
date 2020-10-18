import random
import json

password_dict = {}
forbidden = ["\"", "\\"] # " and \ aren't allowed (special characters)
ascii_range = [chr(i) for i in range(33, 127) if chr(i) not in forbidden] # Get all valid ASCII characters

for password_num in range(100):
    s = ""
    for char_num in range(156):
        s = s + random.choice(ascii_range) # Generate random ASCII character
    password_dict[str(password_num)] = "<~" + s + "~>"

with open("passwords.json", "w") as f:
    json.dump(password_dict, f, indent="\t") # Write password to json file
