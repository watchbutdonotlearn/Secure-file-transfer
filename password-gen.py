from random import random
from math import floor

f = open("passwords.json", "w")
choices = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM`1234567890~!@#$%^&*()-=[];',./_+{}|:<>?"
password_list = []
for password_num in range(100):
    s = ""
    for char_num in range(156):
        s = s + choices[floor(random()*92)]
    password_list.append(s)
f.write("{\n")
for i in range(100):
    f.write("\t\"")
    f.write(str(i))
    f.write("\": \"<~")
    f.write(password_list[i])
    f.write("~>\"")
    if i != 99:
        f.write(",")
    f.write("\n")
f.write("}\n")
f.close()
