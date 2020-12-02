import tkinter as tk 
from tkinter import ttk 
import email, smtplib, ssl
import pyzipper
import random
import json
import platform
import os
import urllib.request
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter.filedialog import askopenfilename

VERSION = ("1", "0", "0a")

def updates_available():
    local_version = VERSION
    if local_version[2][-1] == "a" or local_version[2][-1] == "b":
        local_status = local_version[2][-1]
    else:
        local_status = "r"
    with urllib.request.urlopen("https://raw.githubusercontent.com/watchbutdonotlearn/Secure-file-transfer/main/VERSION.txt")  as f:
        release_version = tuple(f.read().decode().strip("\n").split("."))
        if release_version[2][-1] == "a" or release_version[2][-1] == "b":
            release_status = release_version[2][-1]
        else:
            release_status = "r"
    out_of_date = ("The current version of Secure File Transfer is {};".format(".".join(release_version)), 
            "you are on version {}.".format(".".join(local_version)), 
            "Please update your software.")
    if int(local_version[0]) < int(release_version[0]):
        return out_of_date    
    if int(local_version[1]) < int(release_version[1]):
        return out_of_date    
    if int(local_version[2].strip("ab")) < int(release_version[2].strip("ab")):
        return out_of_date
    if (local_status, release_status) == ("a", "b") or \
            (local_status, release_status) == ("b", "r") or \
            (local_status, release_status) == ("a", "r"):
        return out_of_date
    return None

def move_zip(zip_number):
    if platform.system() == "Windows":
        return "move " + str(zip_number) + ".zip output\\"
    elif platform.system() == "Darwin" or platform.system() == "Linux":
        return "mv " + str(zip_number) + ".zip output/"

def encrypt():
    passfilename = passfilname
    passnum = random.randint(0,99)
    with open(passfilename, "r") as f:
        password_dict = json.load(f)
    zipname = str(passnum) + ".zip"
    zippassword = password_dict[str(passnum)].encode()
    filetosend = sendfilname
    filename_nodirs = filetosend.split("/")[-1]
    with pyzipper.AESZipFile(zipname,
            'w',
            compression=pyzipper.ZIP_LZMA,
            encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(zippassword)
        zf.write(filetosend, filename_nodirs)
    return passnum

def sendemail():
    subject = bSubject
    body = bBody
    sender_email = sEmail
    receiver_email = rEmail
    password = sPass
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    passnum = encrypt()
    filename = str(passnum) + ".zip"
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
            )
    message.attach(part)
    text = message.as_string()
    os.system(move_zip(passnum));
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
        identoutlook = isoutlook
        if identoutlook == 1:
            outlooksend()
            break
        elif identoutlook == 2:
            gmailsend()
            break

def decrypt():
    archivename = decryptarchivename
    passfilename = decryptpasswfilname
    passnum = archivename.strip(".zip")
    passarr = passnum.split('/')
    passarr = passarr[-1]
    with open(passfilename, "r") as f:
        password_dict = json.load(f)
    zippassword = password_dict[passarr].encode()
    with pyzipper.AESZipFile(archivename) as f:
        f.pwd = zippassword
        f.extractall(".")

class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):  
        tk.Tk.__init__(self, *args, **kwargs) 
        container = tk.Frame(self)   
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1) 
        container.grid_columnconfigure(0, weight = 1) 
        self.frames = {}   
        for F in (StartPage, Sending, Receive):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew") 
        self.show_frame(StartPage)
    def show_frame(self, cont): 
        frame = self.frames[cont] 
        frame.tkraise() 

class StartPage(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg='grey94')
        label = ttk.Label(self, text ="Welcome to Secure File Transfer!")
        label.grid(row = 0, column = 1, padx = 10, pady = 10)
        
        button1 = ttk.Button(self, text ="Send Email", command = lambda : controller.show_frame(Sending))
        button1.grid(row = 1, column = 1, padx = 10, pady = 10)
        
        button2 = ttk.Button(self, text ="Decrypt Files", command = lambda : controller.show_frame(Receive))
        button2.grid(row = 2, column = 1, padx = 10, pady = 10)
        
        passconf = tk.StringVar()
        passconf.set("")
        
        def passwordgen():
            password_dict = {}
            forbidden = ["\"", "\\"]
            ascii_range = [chr(i) for i in range(33, 127) if chr(i) not in forbidden]
            for password_num in range(100):
                s = ""
                for char_num in range(156):
                    s = s + random.choice(ascii_range)
                password_dict[str(password_num)] = "<~" + s + "~>"
            with open("passwords.json", "w") as f:
                json.dump(password_dict, f, indent="\t")
            passconf.set("Password File Generated!")
        
        confirmpasswordgen = ttk.Label(self, textvariable=passconf)
        confirmpasswordgen.grid(row = 3, column = 2, padx = 10, pady = 10)
        
        passwordgenbutton = ttk.Button(self, text="Generate Password File", command=passwordgen)
        passwordgenbutton.grid(row = 3, column = 1, padx = 10, pady = 10)

        update = updates_available();
        if update != None:
            for i in range(3):
                ttk.Label(self, text = update[i]).grid(row = i+4, column = 1, padx = 10, pady = 0)

class Sending(tk.Frame): 
      
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.configure(bg='grey94')
        label = ttk.Label(self, text ="Send Email") 
        label.grid(row = 0, column = 1, padx = 2, pady = 10) 
        
        button1 = ttk.Button(self, text ="Start Page", command = lambda : controller.show_frame(StartPage)) 
        button1.grid(row = 1, column = 1, padx = 2, pady = 10) 
        
        button2 = ttk.Button(self, text ="Decrypt Files", command = lambda : controller.show_frame(Receive)) 
        button2.grid(row = 2, column = 1, padx = 2, pady = 10) 
        
        senderemaillabel = ttk.Label(self, text ="Input sender email address here")
        senderemaillabel.grid(row = 3, column = 1, padx = 2, pady = 5)
        
        senderemailbox = ttk.Entry(self, width=50)
        senderemailbox.grid(row = 3, column = 3, padx = 10, pady = 5)
        
        receiveremaillabel = ttk.Label(self, text ="Input receiver email address here")
        receiveremaillabel.grid(row = 5, column = 1, padx = 9, pady = 5)
        
        receiveremailbox = ttk.Entry(self, width=50)
        receiveremailbox.grid(row = 5, column = 3, padx = 11, pady = 5)
        
        passwordlabel = ttk.Label(self, text ="Input password")
        passwordlabel.grid(row = 7, column = 1, padx = 2, pady = 5)
        
        passwordbox = ttk.Entry(self, show="*", width=50)
        passwordbox.grid(row = 7, column = 3, padx = 10, pady = 5)
        
        subjectlabel = ttk.Label(self, text ="Input subject line")
        subjectlabel.grid(row = 8, column = 1, padx = 2, pady = 5)
        
        subjectbox = ttk.Entry(self, width=50)
        subjectbox.grid(row = 8, column = 3, padx = 10, pady = 5)
        
        bodylabel = ttk.Label(self, text ="Input body text")
        bodylabel.grid(row = 9, column = 1, padx = 2, pady = 5)
        
        bodybox = ttk.Entry(self, width=50)
        bodybox.grid(row = 9, column = 3, padx = 10, pady = 5)
        
        string_1 = tk.StringVar()
        string_1.set("")
        
        def choosepassfilebutton():
            global passfilname
            passfilname = askopenfilename()
            string_1.set(str(passfilname))
        
        passfilebuttonshow = ttk.Label(self, textvariable=string_1)
        passfilebuttonshow.grid(row = 10, column = 3, padx = 1, pady = 10)
        
        passfilebutton = ttk.Button(self, text="Choose Password File", command=choosepassfilebutton)
        passfilebutton.grid(row = 10, column = 1, padx = 1, pady = 10)
        
        string_2 = tk.StringVar()
        string_2.set("")
        
        def choosesendfilebutton():
            global sendfilname
            sendfilname = askopenfilename()
            string_2.set(str(sendfilname))
        
        sendfilebutton = ttk.Button(self, text="Choose File to Send", command=choosesendfilebutton)
        sendfilebutton.grid(row = 11, column = 1, padx = 1, pady = 10)
        
        sendfilebuttonshow = ttk.Label(self, textvariable=string_2)
        sendfilebuttonshow.grid(row = 11, column = 3, padx = 1, pady = 10)
        
        string_5 = tk.StringVar()
        string_5.set("Outlook or Gmail:")
        isoutlook = 1
        
        def gmailbutton():
            string_5.set("Outlook or Gmail: Gmail")
            global isoutlook
            isoutlook = 2
        
        def outlookbutton():
            string_5.set("Outlook or Gmail: Outlook")
            global isoutlook
            isoutlook = 1
        
        outlookgmaillabel = ttk.Label(self, textvariable=string_5)
        outlookgmaillabel.grid(row = 12, column = 1, padx = 1, pady = 5)
        
        dooutlookbutton = ttk.Button(self, text="Outlook", command=outlookbutton)
        dooutlookbutton.grid(row = 13, column = 1, padx = 10, pady = 5)
        
        dogmailbutton = ttk.Button(self, text="Gmail", command=gmailbutton)
        dogmailbutton.grid(row = 13, column = 3, padx = 10, pady = 5)
        
        sendconf = tk.StringVar()
        sendconf.set("")
        
        def sendtheemail():
            global sPass
            global sEmail
            global rEmail
            global bBody
            global bSubject
            
            try:
                sPass = passwordbox.get()
                rEmail = receiveremailbox.get()
                sEmail = senderemailbox.get()
                bBody = bodybox.get()
                bSubject=subjectbox.get()
                sendemail()
                sendconf.set("Email successfully sent!")
            except:
                sendconf.set("Unsuccessful in sending")
        
        sendmailconfl = ttk.Label(self, textvariable=sendconf)
        sendmailconfl.grid(row = 14, column = 3)
        
        Sendemailbutton = ttk.Button(self, text="Send Email", command=sendtheemail)
        Sendemailbutton.grid(row = 14, column = 1, padx = 10, pady = 10)

class Receive(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        self.configure(bg='grey94')
        label = ttk.Label(self, text ="Decrypt Files")
        label.grid(row = 0, column = 1, padx = 56, pady = 10)
        
        button1 = ttk.Button(self, text ="Send Email", command = lambda : controller.show_frame(Sending))
        button1.grid(row = 1, column = 1, padx = 59, pady = 10)
        
        button2 = ttk.Button(self, text ="Start Page", command = lambda : controller.show_frame(StartPage))
        button2.grid(row = 2, column = 1, padx = 56, pady = 10)
        
        string_3 = tk.StringVar()
        string_3.set("")
        
        def decryptarchivenamebutton():
            global decryptarchivename
            decryptarchivename = askopenfilename()
            string_3.set(str(decryptarchivename))
        
        decryptarchivebutton = ttk.Button(self, text="Choose File to Decrypt", command=decryptarchivenamebutton)
        decryptarchivebutton.grid(row = 3, column = 1, padx = 1, pady = 10)
        
        decryptlabel = ttk.Label(self, textvariable=string_3)
        decryptlabel.grid(row = 3, column = 2, padx = 1, pady = 10)
        
        string_4 = tk.StringVar()
        string_4.set("")
        
        def decryptpassfilename():
            global decryptpasswfilname
            decryptpasswfilname = askopenfilename()
            string_4.set(str(decryptpasswfilname))
        
        passfilebuttonshow = ttk.Label(self, textvariable=string_4)
        passfilebuttonshow.grid(row = 4, column = 2, padx = 1, pady = 10)
        
        passfilebutton = ttk.Button(self, text="Choose Password File", command=decryptpassfilename)
        passfilebutton.grid(row = 4, column = 1, padx = 1, pady = 10)
        
        decryptconf = tk.StringVar()
        decryptconf.set('')
        
        def dodecryptbutton():
            try:
                decrypt()
                decryptconf.set('File successfully decrypted!')
            except:
                decryptconf.set('Unsuccessful decryption')
        
        confirmdecryptl = ttk.Label(self, textvariable=decryptconf)
        confirmdecryptl.grid(row = 5, column = 2)
        
        decryptbutton = ttk.Button(self, text="Decrypt", command=dodecryptbutton)
        decryptbutton.grid(row = 5, column =1, padx = 1, pady = 10)

app = tkinterApp()
app.title("Secure File Transfer")
if platform.system() == "Windows":
    photo = tk.PhotoImage(file = "icon.png")
    app.iconphoto(False, photo)
app.mainloop()
