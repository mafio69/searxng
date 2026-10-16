export const HISTORY_KEY = 'szukaj.history.v1';
export const PRIVATE_KEY = 'szukaj.private.v1';

export function readHistory() {
  try {
    const data = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    return Array.isArray(data) ? data.filter(item =>
      item && typeof item.query === 'string' && item.query.trim() &&
      Number.isFinite(item.time)).slice(0, 30) : [];
  } catch { return []; }
}

export function remember(history, query, time = Date.now()) {
  return [{ query, time }, ...history.filter(item =>
    item.query.toLocaleLowerCase('pl') !== query.toLocaleLowerCase('pl'))].slice(0, 30);
}

export function store(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); return true; }
  catch { return false; }
}

export function readPrivate() {
  try { return localStorage.getItem(PRIVATE_KEY) === 'true'; }
  catch { return false; }
}
