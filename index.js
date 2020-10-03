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

  let main = arg.split(`<br>`)
  let sendName = main[0].split(`text-`)[1]
  let email = main[1].split(`email-`)[1]
  let filetotransfer = main[2].split(`file-`)[1]
  let passwordfile = require(main[3].split(`file-`)[1])
  let passnumber = Math.floor(Math.random() * Object.keys(passwordfile).length);
  let code = passwordfile[passnumber]

  console.log(`Using email: ` + email + `\nSending the file: ${filetotransfer.split("/").pop()}\nUsing the passwordfile: ${main[2].split(`file-`)[1].split("/").pop()}\nWith the password number of: ${passnumber}\nWhich equals: ${code}`)

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
      secure: true,
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


// Other Functions:
function encode_ascii85(a) {
    var b, c, d, e, f, g, h, i, j, k;
    for (!/[^\x00-\xFF]/.test(a), b = "\x00\x00\x00\x00".slice(a.length % 4 || 4), a += b, 
    c = [], d = 0, e = a.length; e > d; d += 4) f = (a.charCodeAt(d) << 24) + (a.charCodeAt(d + 1) << 16) + (a.charCodeAt(d + 2) << 8) + a.charCodeAt(d + 3), 
    0 !== f ? (k = f % 85, f = (f - k) / 85, j = f % 85, f = (f - j) / 85, i = f % 85, 
    f = (f - i) / 85, h = f % 85, f = (f - h) / 85, g = f % 85, c.push(g + 33, h + 33, i + 33, j + 33, k + 33)) :c.push(122);
    return function(a, b) {
      for (var c = b; c > 0; c--) a.pop();
    }(c, b.length), "<~" + String.fromCharCode.apply(String, c) + "~>";
  }

function decode_ascii85(a) {
  var c, d, e, f, g, h = String, l = "length", w = 255, x = "charCodeAt", y = "slice", z = "replace";
  for ("<~" === a[y](0, 2) && "~>" === a[y](-2), a = a[y](2, -2)[z](/\s/g, "")[z]("z", "!!!!!"), 
  c = "uuuuu"[y](a[l] % 5 || 5), a += c, e = [], f = 0, g = a[l]; g > f; f += 5) d = 52200625 * (a[x](f) - 33) + 614125 * (a[x](f + 1) - 33) + 7225 * (a[x](f + 2) - 33) + 85 * (a[x](f + 3) - 33) + (a[x](f + 4) - 33), 
  e.push(w & d >> 24, w & d >> 16, w & d >> 8, w & d);
  return function(a, b) {
    for (var c = b; c > 0; c--) a.pop();
  }(e, c[l]), h.fromCharCode.apply(h, e);
}

function reload(file) {
  delete require.cache[require.resolve(file)];
  return require(file);
}