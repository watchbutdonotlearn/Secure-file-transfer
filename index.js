// Variables:
const fs = require("fs")
const { app, BrowserWindow, ipcMain, nativeImage, globalShortcut } = require('electron')
const os = require(`os`)
const nodemailer = require("nodemailer");
let storage = fs.readFileSync(`./assets/storage.txt`, {encoding:'utf8'})

// Generate passwords:
// let passwordfil = require(`./test/test.json`)

// for(let l = 0; l < 100; l++) {

//     var result           = '';
//     var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
//     var charactersLength = characters.length;
//     for ( var i = 0; i < charactersLength; i++ ) {
//         result += characters.charAt(Math.floor(Math.random() * charactersLength));
//     }
//     passwordfil[l] = encode_ascii85(result);
// }

// fs.writeFileSync(`./test/test.json`, JSON.stringify(passwordfil, null, 2));

// GUI:

var image = nativeImage.createFromPath(__dirname + '/assets/Icon.ico'); 
image.setTemplateImage(true);

function createWindow () {
    const win = new BrowserWindow({
      webPreferences: {
        // devTools: false,
        nodeIntegration: true
      },
      icon: image
    })

    win.setMenuBarVisibility(false)
    if(storage.split(`\n`)[1]) win.loadFile('./index.html')
    else win.loadFile('./new.html')
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

//   app.on(`ready`, () => {
//     globalShortcut.register(`Control+Shift+I`, () => {})
//   })
  
// Login:
ipcMain.on('login', function(event, email, pass) {

  let text = ""
  text += email + `\n`
  text += pass

  fs.writeFileSync(`./assets/storage.txt`, text);

});

let archive = null;
  // Clicking
  ipcMain.on('sendclicked', function(event, arg) {

    let main = arg.split(`<br>`)
    let email = main[0].split(`email-`)[1]
    let filetotransfer = main[1].split(`file-`)[1]
    let passwordfile = require(main[2].split(`file-`)[1])

    let passnumber = Math.floor(Math.random() * Object.keys(passwordfile).length);

    let code = passwordfile[passnumber]

    console.log(email, `\n`, filetotransfer.split("/").pop(), `\n`, main[2].split(`file-`)[1].split("/").pop(), `\n`, passnumber, `\n`, code)

    var archiver = require('archiver');
 
    if(!archive) archiver.registerFormat('zip-encryptable', require('archiver-zip-encryptable'));
     
    var output = fs.createWriteStream(__dirname + '/test/output.zip');
     
    archive = archiver('zip-encryptable', {
        zlib: { level: 9 },
        forceLocalTime: true,
        password: code
    });

    archive.pipe(output);
    archive.file(filetotransfer, {name: filetotransfer.split("/").pop()});

    archive.append(Buffer.from(" "), {name: `${passnumber}.txt`})

    archive.finalize();      

    sendemail()      

    async function sendemail() {
      storage = fs.readFileSync(`./assets/storage.txt`, {encoding:'utf8'})
      let array = storage.split(`\n`)
      console.log(array.join(`, `))
      let email2 = array[0]
      let pass = array[1]

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

        from: `Sender Name <${email2}>`,
        to: `"Receiver Name" <${email}>`,
        subject: 'Secure File Transfer', 
        text: 'This is a Secure File Transfer!',
        attachments: [
          {
              filename: 'output.zip',
              path: __dirname + '/test/output.zip'
          }
        ]
    };
    
    console.log('Sending Mail');
    transport.sendMail(message, function(error){
      if(error){
          console.log('Error occured');
          console.log(error.message);
          return;
      }
      console.log('Message sent successfully!');

      })
  }
});


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