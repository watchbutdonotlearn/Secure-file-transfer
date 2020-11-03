import email, smtplib, ssl
import pyzipper
import json
from random import randint
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def encrypt():
    passfilename = input("Input the name of the password file here: ")
    passnum = randint(0,99)
    with open(passfilename, "r") as f:
        password_dict = json.load(f)
    print("Password number " + str(passnum) + " is " + password_dict[str(passnum)])
    zipname = str(passnum) + ".zip"
    zippassword = password_dict[str(passnum)].encode()
    filetosend = input("Input the name of the file you want to send: ")
    with pyzipper.AESZipFile(zipname,
            'w',
            compression=pyzipper.ZIP_LZMA,
            encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(zippassword)
        zf.write(filetosend)
    return zipname

def sendemail():
    subject = input("Type subject here: ")
    body = input("Type body text here: ")
    sender_email = input("Type sender email here: ")
    receiver_email = input("Type the receiver email here: ")
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

    # Log in to server using secure context and send email GMAIL
    def gmailsend():
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

    def outlooksend():
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

    while True:
        identoutlook = int(input("If you are using outlook, type 1, if you are using Gmail, type 2: "))
        if identoutlook == 1:
            outlooksend()
            break
        elif identoutlook == 2:
            gmailsend()
            break
        else:
            print("Please enter 1 or 2")
    print("Your email has been sent")

def decrypt():
    archivename = input("Input the name of the archive you want to decrypt: ")
    passfilename = input("Input the name of the password file here: ")
    passnum = archivename.strip(".zip")
    with open(passfilename, "r") as f:
        password_dict = json.load(f)
    print("Password number " + passnum + " is " + password_dict[passnum])
    zippassword = password_dict[passnum].encode()
    with pyzipper.AESZipFile(archivename) as f:
        f.pwd = zippassword
        print(f.infolist())
        print(f.filename)
        f.extractall(".")
    print("Your file has been extracted")

while True:
    selector = int(input("Type 1 for sending emails, type 2 for receiving emails, type 3 to only generate an encrypted file without sending an email, and type 4 to exit: "))

    if selector == 1:
        sendemail()

    elif selector == 2:
        decrypt()

    elif selector == 3:
        encrypt()

    elif selector == 4:
        break
    
    else:
        print("Please enter a number from 1 to 4")

print("Thank you for using Secure File Transfer")

