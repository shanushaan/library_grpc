const WebSocket = require('ws');

let wss;
const userConnections = new Map();

const initWebSocket = (server) => {
  wss = new WebSocket.Server({ server });
  
  wss.on('connection', (ws, req) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const userId = url.searchParams.get('userId');
    
    if (userId) {
      userConnections.set(userId, ws);
      console.log(`User ${userId} connected`);
    }
    
    ws.on('close', () => {
      if (userId) {
        userConnections.delete(userId);
        console.log(`User ${userId} disconnected`);
      }
    });
  });
};

const sendNotification = (userId, notification) => {
  const ws = userConnections.get(userId.toString());
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(notification));
  }
};

module.exports = { initWebSocket, sendNotification };