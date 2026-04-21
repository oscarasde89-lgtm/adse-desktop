const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('adse', {
  login: (email, password) => ipcRenderer.invoke('licencia:login', { email, password }),
  abrir: () => ipcRenderer.invoke('licencia:abrir'),
  salir: () => ipcRenderer.invoke('licencia:salir'),
});
