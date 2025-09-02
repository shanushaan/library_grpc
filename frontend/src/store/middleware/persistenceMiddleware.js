export const persistenceMiddleware = (store) => (next) => (action) => {
  const result = next(action);
  
  // Persist specific slices to localStorage
  const state = store.getState();
  const persistedState = {
    users: state.users,
    books: state.books,
    bookRequests: state.bookRequests,
  };
  
  try {
    localStorage.setItem('redux-state', JSON.stringify(persistedState));
  } catch (error) {
    console.warn('Failed to persist state:', error);
  }
  
  return result;
};

export const loadPersistedState = () => {
  try {
    const serializedState = localStorage.getItem('redux-state');
    if (serializedState === null) {
      return undefined;
    }
    return JSON.parse(serializedState);
  } catch (error) {
    console.warn('Failed to load persisted state:', error);
    return undefined;
  }
};