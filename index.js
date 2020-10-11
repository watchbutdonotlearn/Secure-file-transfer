// Variables:
const fs = require("fs")
const { app, BrowserWindow, ipcMain, nativeImage, globalShortcut, webContents } = require('electron')
const os = require(`os`)
const nodemailer = require("nodemailer");
let appdatadir = process.env.APPDATA || (process.platform == 'darwin' ? process.env.HOME + '/Library/Preferences' : process.env.HOME + "/.local/share")
appdatadir += `/securefiletransfer`
const unzipper = require(`unzipper`);
let archive;

const request = require('request');

const download = (url, path, callback) => {
  request.head(url, (err, res, body) => {
    request(url)
      .pipe(fs.createWriteStream(path))
      .on('close', callback)
  })
}

if(!fs.existsSync(appdatadir)) {
  fs.mkdirSync(appdatadir);
  fs.mkdirSync(appdatadir + `/assets`)
  fs.mkdirSync(appdatadir + `/output`)
  fs.writeFileSync(appdatadir + `/assets/storage.txt`, "")
  download(`https://cdn.discordapp.com/attachments/675039532026036261/762033994032218122/Icon.ico`, `${appdatadir}/assets/Icon.ico`, function() {console.log(`Downloaded the icon.`)})
}

if(!fs.existsSync(appdatadir + `/assets/storage.txt`)) {
  fs.writeFileSync(appdatadir + `/assets/storage.txt`, "")
}
if(!fs.existsSync(appdatadir + `/assets/Icon.ico`)) {
  download(`https://cdn.discordapp.com/attachments/675039532026036261/762033994032218122/Icon.ico`, `${appdatadir}/assets/Icon.ico`, function() {console.log(`Downloaded the icon.`)})
}

let storage = fs.readFileSync(appdatadir + `/assets/storage.txt`, {encoding:'utf8'})

// Generate passwords:
// let passwordfil = require(`./output/passwords.json`)

// for(let l = 0; l < 250; l++) {

//     var result           = '';
//     var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
//     var charactersLength = characters.length;
//     for ( var i = 0; i < 100; i++ ) {
//         result += characters.charAt(Math.floor(Math.random() * charactersLength));
//     }
//     passwordfil[l] = encode_ascii85(result);
// }

// fs.writeFileSync(`./output/passwords.json`, JSON.stringify(passwordfil, null, 2));

// GUI:

var image = nativeImage.createFromPath(appdatadir + '/assets/Icon.ico'); 
image.setTemplateImage(true);
let win;

function createWindow () {
    win = new BrowserWindow({
      webPreferences: {
        // devTools: false,
        nodeIntegration: true
      },
      icon: image
    })

    win.setMenuBarVisibility(false)
    if(storage.split(`\n`)[2]) win.loadFile('./decrypter.html')
    else win.loadFile('./setup.html')
  }
  
  app.whenReady().then(createWindow)
  
  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit()
    }
  })
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })

  app.on(`ready`, () => {
    globalShortcut.register(`Control+Shift+I`, () => {})
  })
  
// Login:
ipcMain.on('login', function(event, email, pass, name) {

  let text = ""
  text += email + `\n`
  text += pass + `\n`
  text += name

  fs.writeFileSync(appdatadir + `/assets/storage.txt`, text);
  win.webContents.send('loginsuccess')

});

ipcMain.on('sendclicked', function(event, arg) {

  let main = arg.split(`<br>`);
  let sendName = main[0].substring(5);
  let email = main[1].substring(6);
  let filetotransfer = main[2].substring(5);
  let passwordpath = main[3].substring(5);
  let passwordfile = require(passwordpath);
  let passnumber = Math.floor(Math.random() * Object.keys(passwordfile).length);
  let code = passwordfile[passnumber]

  console.log(`Using email: ` + email + `\nSending the file: ${filetotransfer.split("/").pop()}\nUsing the passwordfile: ${passwordpath.split("/").pop()}\nWith the password number of: ${passnumber}\nWhich equals: ${code}`)

  var archiver = require('archiver');

  if(!archive) archiver.registerFormat('zip-encryptable', require('archiver-zip-encryptable'));
     
  var output = fs.createWriteStream(appdatadir + `/output/${passnumber}.zip`);
     
  archive = archiver('zip-encryptable', {
    zlib: { level: 9 },
    forceLocalTime: true,
    password: code
  });

  archive.pipe(output);
  archive.file(filetotransfer, {name: filetotransfer.split("/").pop()});

  archive.finalize();      

  sendemail()      

  async function sendemail() {
    storage = fs.readFileSync(appdatadir + `/assets/storage.txt`, {encoding:'utf8'})
    let array = storage.split(`\n`)
    let email2 = array[0]
    let pass = array[1]
    let myName = array[2]

    var transport = nodemailer.createTransport({
      service: `hotmail`,
      auth: {
        user: email2,
        pass: pass
      },
      tls: {
        ciphers:'SSLv3'
    }
    });

    var message = {

      from: `"${myName}" <${email2}>`,
      to: `"${sendName}" <${email}>`,
      subject: 'Secure File Transfer', 
      text: 'This is a Secure File Transfer!',
      attachments: [
        {
          filename: `${passnumber}.zip`,
          path: appdatadir + `/output/${passnumber}.zip`
        }
      ]
    };
    
    console.log('Sending Mail');
    transport.sendMail(message, function(error){
      if(error){
          console.log('Error occured');
          console.log(error.message);
          win.webContents.send('email', false)
          return;
      }
      console.log('Message sent successfully!');
      win.webContents.send('email', true)
      fs.unlinkSync(appdatadir + `/output/${passnumber}.zip`)
      
      })
  }
});

ipcMain.on('decryptclicked', async function(event, filetotransfer, passwordfile) {
  
  let passfile = require(passwordfile)
  let pas = filetotransfer.split("\\").pop()
  let pass = passfile[pas.replace(`.zip`, ``)]
  if(!pass) return console.log(`No pass! ${pas}, ${pas.replace(`.zip`, ``)}, ${passfile[filetotransfer.split(`/`).pop().replace(`.zip`, ``)]}`)

  main(filetotransfer)

  async function main (a) {
    try {
      const directory = await unzipper.Open.file(a);
      const extracted = await directory.files.forEach(file => {
        let filename = file.path.split(`/`).pop().toString()
        file.stream(pass)
        .pipe(fs.createWriteStream(`./output/`+filename))
        .on('error', () => {
           console.log('error on unzipping');
           win.webContents.send('decrypt', `${filename}`, `err`)
        })
        .on('finish', () => {
            console.log(`Successfully Unzipping: ${filename}`);
            win.webContents.send('decrypt', `${filename}`, `no err`)
        })
      })
      require('child_process').exec(`start "" "${appdatadir}/output/"`);
    } catch(e) {
      console.log(e);
    }
  };
   
})
