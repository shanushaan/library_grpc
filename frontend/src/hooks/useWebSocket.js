import { useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { showNotification } from '../store/slices/uiSlice';

export const useWebSocket = (user) => {
  const ws = useRef(null);
  const dispatch = useDispatch();

  useEffect(() => {
    if (!user?.user_id) return;

    const wsUrl = `ws://localhost:8001?userId=${user.user_id}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      dispatch(showNotification({
        message: notification.message,
        type: notification.type === 'REQUEST_APPROVED' ? 'success' : 'error'
      }));
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [user, dispatch]);

  return ws.current;
};