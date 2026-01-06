const { app, BrowserWindow, shell } = require('electron');
const path = require('path');

const isDev = process.argv.includes('--dev');
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: path.join(__dirname, '../frontend/apps/web/public/vite.svg')
  });

  if (isDev) {
    // Load Vite dev server in development
    mainWindow.loadURL('http://localhost:5173');
  } else {
    // Load built app in production
    mainWindow.loadURL(`file://${path.join(__dirname, '../frontend/apps/web/dist/index.html')}`);
  }

  // Open external links in the default browser
  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: 'deny' };
  });

 if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(() => {
 createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});