import email, smtplib, ssl
import pyzipper
import json
import random
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def encrypt():
    passfilename = input("Input the name of the password file here: ")
    passnum = random.randint(0, 99)
    with open(passfilename, 'r') as f:
        password_dict = json.load(f)
    print("Password number " + str(passnum) + " is " + password_dict[str(passnum)])
    passn = str(passnum) + ".zip"
    passw = password_dict[str(passnum)].encode()
    password = passw
    filetosend = input("Input the name of the file you want to send: ")
    with pyzipper.AESZipFile(passn,
            'w',
            compression=pyzipper.ZIP_LZMA,
            encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password)
        zf.write(filetosend)
    return passn

# send the email
def sendemail():
    subject = input("Type subject here: ")
    body = input("Type body text here: ")
    sender_email = input("Type sender email here: ")
    receiver_email = input("Type the reciever email here: ")
    password = input("Type your password and press enter: ")
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    filename = encrypt()
    
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    
    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

def decrypt():
    archivename = input('Input the name of the archive you want to decrypt: ')
    passfilename = input('Input the name of the password file here: ')
    #passnum = input('TEMPORARY input the password number here:') # FIX THIS AND MAKE IT READ PASS NUMBER FROM NAME OF FILE
    passnum = archivename.strip(".zip")
    with open(passfilename, "r") as f:
        password_dict = json.load(f)
    print("Password number " + str(passnum) + " is " + password_dict[str(passnum)])
    passn2 = str(passnum)
    passw2 = password_dict[str(passnum)].encode()
    password1 = passw2
    with pyzipper.AESZipFile(archivename) as f:
        f.pwd = password1
        print(f.infolist())
        print(f.filename)
        f.extractall(".")

while True:
    selector = int(input("Type 1 for sending emails, type 2 for recieving emails, type 3 to exit: "))
    
    if selector == 1:
        sendemail()
    
    if selector == 2:
        decrypt()
    
    if selector == 3:
        break

print("Thanks for using the Secure File Transfer!")
