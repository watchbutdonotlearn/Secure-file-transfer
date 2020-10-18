import email, smtplib, ssl
import pyzipper
import json
from random import randint
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def encrypt():
    passfilename = input('input the name of the password file here:')
    passnum = randint(0,99)
    with open(passfilename, "r") as f:
        password_dict = json.load(f)
    print("Password number " + str(passnum) + " is " + password_dict[str(passnum)])
    global passw
    global passn
    passn = str(passnum) + '.zip'
    passw = password_dict[str(passnum)].encode()
    password = passw
    filetosend = input("input the name of the file you want to send:")
    with pyzipper.AESZipFile(passn,
            'w',
            compression=pyzipper.ZIP_LZMA,
            encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password)
        zf.write(filetosend)

def sendemail():
    subject = input("type subject here:")
    body = input("type body text here:")
    sender_email = input("type sender email here:")
    receiver_email = input("type the reciever email here:")
    password = input("Type your password and press enter:")
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    encrypt()
    
    # filename = "a.txt"  # In same directory as script
    filename = passn
    
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
    
    identoutlook = int(input('If you are using outlook, type 1, if you are using Gmail, type 2:'))
    
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
    
    if identoutlook == 1:
        outlooksend()
    if identoutlook == 2:
        gmailsend()

def decrypt():
    archivename = input('input the name of the archive you want to decrypt:')
    passfilename = input('input the name of the password file here:')
    passnum = input('TEMPORARY input the password number here:') # FIX THIS AND MAKE IT READ PASS NUMBER FROM NAME OF FILE
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
    selector = int(input("Type 1 for sending emails, type 2 for recieving emails, type 3 to only generate an encrypted file without sending an email, and type 4 to exit:"))
    
    if selector == 1:
        sendemail()
    
    if selector == 2:
        decrypt()
    
    if selector == 3:
        encrypt()
    
    if selector == 4:
        break

print('Thank you for using Secure File Transfer')
