import tkinter as tk 
from tkinter import ttk 
import email, smtplib, ssl
import pyzipper
import json
from random import randint
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter.filedialog import askopenfilename

def encrypt():
    passfilename = passfilname
    passnum = randint(0,99)
    with open(passfilename, "r") as f:
        password_dict = json.load(f)
    print("Password number " + str(passnum) + " is " + password_dict[str(passnum)])
    zipname = str(passnum) + ".zip"
    zippassword = password_dict[str(passnum)].encode()
    filetosend = sendfilname
    filename_nodirs = filetosend.split('/')[-1]
    with pyzipper.AESZipFile(zipname,
            'w',
            compression=pyzipper.ZIP_LZMA,
            encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(zippassword)
        zf.write(filetosend, filename_nodirs)
    return zipname

def sendemail():
    subject = 'Something' # Maybe replace with something different? 
    body = 'Something' # same as before, replace something with something differnet
    sender_email = sEmail
    receiver_email = rEmail
    password = sPass
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email
    
    message.attach(MIMEText(body, "plain"))

    filename = encrypt()

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
    print("Your email has been sent")

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
    print("Your file has been extracted to " + archivename)

class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):  
        tk.Tk.__init__(self, *args, **kwargs) 
        container = tk.Frame(self)   
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1) 
        container.grid_columnconfigure(0, weight = 1) 
        self.frames = {}   
        for F in (StartPage, Page1, Page2):
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
        
        label = ttk.Label(self, text ="Welcome to Secure File Transfer!")
        label.grid(row = 0, column = 1, padx = 10, pady = 10)
   
        button1 = ttk.Button(self, text ="Send Email",
        command = lambda : controller.show_frame(Page1))
        button1.grid(row = 1, column = 1, padx = 10, pady = 10)
   
        button2 = ttk.Button(self, text ="Decrypt Files",
        command = lambda : controller.show_frame(Page2))
        button2.grid(row = 2, column = 1, padx = 10, pady = 10)

class Page1(tk.Frame): 
      
    def __init__(self, parent, controller): 
        
        tk.Frame.__init__(self, parent) 
        label = ttk.Label(self, text ="Send emails") 
        label.grid(row = 0, column = 1, padx = 2, pady = 10) 
        
        button1 = ttk.Button(self, text ="Start Page", 
                            command = lambda : controller.show_frame(StartPage)) 
        button1.grid(row = 1, column = 1, padx = 2, pady = 10) 
        
        button2 = ttk.Button(self, text ="Recieve Emails", 
                            command = lambda : controller.show_frame(Page2)) 
        button2.grid(row = 2, column = 1, padx = 2, pady = 10) 
        
        senderemaillabel = ttk.Label(self, text ="Input sender email address here")
        senderemaillabel.grid(row = 3, column = 1, padx = 2, pady = 1)
        
        senderemailbox = ttk.Entry(self)
        senderemailbox.grid(row = 3, column = 3, padx = 10, pady = 1)
        
        recieveremaillabel = ttk.Label(self, text ="Input reciever email address here")
        recieveremaillabel.grid(row = 5, column = 1, padx = 2, pady = 1)
        
        recieveremailbox = ttk.Entry(self)
        recieveremailbox.grid(row = 5, column = 3, padx = 10, pady = 10)
        
        passwordlabel = ttk.Label(self, text ="Input password")
        passwordlabel.grid(row = 7, column = 1, padx = 2, pady = 1)
        
        passwordbox = ttk.Entry(self)
        passwordbox.grid(row = 7, column = 3, padx = 10, pady = 10)
        
        string_1 = tk.StringVar()
        string_1.set("")
        
        def choosepassfilebutton():
            global passfilname
            passfilname = askopenfilename()
            string_1.set(str(passfilname))
        
        passfilebuttonshow = ttk.Label(self, textvariable=string_1)
        passfilebuttonshow.grid(row = 8, column = 3, padx = 1, pady = 10)
        
        passfilebutton = ttk.Button(self, text="choose password file", command=choosepassfilebutton)
        passfilebutton.grid(row = 8, column = 1, padx = 1, pady = 10)
        
        string_2 = tk.StringVar()
        string_2.set("")
        
        def choosesendfilebutton():
            global sendfilname
            sendfilname = askopenfilename()
            string_2.set(str(sendfilname))
        
        sendfilebutton = ttk.Button(self, text="choose file to send", command=choosesendfilebutton)
        sendfilebutton.grid(row = 9, column = 1, padx = 1, pady = 10)
        
        sendfilebuttonshow = ttk.Label(self, textvariable=string_2)
        sendfilebuttonshow.grid(row = 9, column = 3, padx = 1, pady = 10)
        
        string_5 = tk.StringVar()
        string_5.set("Outlook or gmail:")
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
        outlookgmaillabel.grid(row = 11, column = 1, padx = 1, pady = 10)
        
        dooutlookbutton = ttk.Button(self, text="outlook", command=outlookbutton)
        dooutlookbutton.grid(row = 12, column = 1, padx = 10)
        
        dogmailbutton = ttk.Button(self, text="gmail", command=gmailbutton)
        dogmailbutton.grid(row = 12, column = 3, padx = 10)
        
        def sendtheemail():
            global sPass
            global sEmail
            global rEmail
            sPass = passwordbox.get()
            rEmail = recieveremailbox.get()
            sEmail = senderemailbox.get()
            sendemail()
        
        Sendemailbutton = ttk.Button(self, text="Send Email", command=sendtheemail)
        Sendemailbutton.grid(row = 14, column = 1, padx = 10, pady = 10)

class Page2(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = ttk.Label(self, text ="Decrypt emails")
        label.grid(row = 0, column = 1, padx = 10, pady = 10)
        
        button1 = ttk.Button(self, text ="Send Emails", 
                            command = lambda : controller.show_frame(Page1))
        button1.grid(row = 1, column = 1, padx = 10, pady = 10)
        
        button2 = ttk.Button(self, text ="Startpage", 
                            command = lambda : controller.show_frame(StartPage))
        button2.grid(row = 2, column = 1, padx = 10, pady = 10)
        
        string_3 = tk.StringVar()
        string_3.set("")
        
        def decryptarchivenamebutton():
            global decryptarchivename
            decryptarchivename = askopenfilename()
            string_3.set(str(decryptarchivename))
        
        decryptarchivebutton = ttk.Button(self, text="choose file to decrypt", command=decryptarchivenamebutton)
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
        
        passfilebutton = ttk.Button(self, text="choose password file", command=decryptpassfilename)
        passfilebutton.grid(row = 4, column = 1, padx = 1, pady = 10)
        
        def dodecryptbutton():
            decrypt()
        
        decryptbutton = ttk.Button(self, text="Decrypt", command=dodecryptbutton)
        decryptbutton.grid(row = 5, column =1, padx = 1, pady = 10)

app = tkinterApp()
app.title("Secure File Transfer")
app.mainloop()
