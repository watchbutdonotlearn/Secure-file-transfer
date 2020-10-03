from random import choice

password_list = []
forbidden = ["\"", "\\"] # " and \ aren't allowed (special characters)
ascii_range = [chr(i) for i in range(33, 127) if chr(i) not in forbidden] # Get all valid ASCII characters

for password_num in range(100):
    s = ""
    for char_num in range(156):
        s = s + choice(ascii_range) # Generate random ASCII character
    password_list.append(s)
    print(s)

with open("passwords.json", "w") as f:
    f.write("{\n")
    for i in range(100):
        f.write("\t\"" + str(i) + "\": \"<~" + password_list[i] + "~>\"") # Write password to json file
        if i != 99:
            f.write(",")
        f.write("\n")
    f.write("}\n")
