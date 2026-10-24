const DEV_MODES = ['dev', 'development', 'local'];
const GENERIC_ERROR_MESSAGE = 'Wystąpił problem techniczny. Spróbuj ponownie za moment.';

export class UserFacingError extends Error {
  constructor(message, detail = '') {
    super(message);
    this.name = 'UserFacingError';
    this.detail = detail;
  }
}

export function isDevMode(envOverride) {
  const raw = envOverride ?? import.meta.env?.VITE_APP_ENV ?? '';
  return DEV_MODES.includes(String(raw).trim().toLowerCase());
}

export function formatSearchError(failure, envOverride) {
  if (failure?.name === 'AbortError') {
    return 'Wyszukiwanie trwało zbyt długo. Spróbuj ponownie.';
  }
  if (failure instanceof UserFacingError) {
    return failure.detail ? `${failure.message} (${failure.detail})` : failure.message;
  }
  if (isDevMode(envOverride) && failure?.message) {
    return `${GENERIC_ERROR_MESSAGE} (${failure.message})`;
  }
  return GENERIC_ERROR_MESSAGE;
}

function isValidItem(item) {
  if (!item || typeof item !== 'object' || Array.isArray(item)) return false;
  return ['title', 'url', 'snippet'].every(field => item[field] == null || typeof item[field] === 'string');
}

export function isValidResult(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) return false;
  if (!['searxng', 'perplexity-fast', null].includes(data.source)) return false;
  if (!Array.isArray(data.results)) return false;
  return data.results.every(isValidItem);
}

async function readErrorDetail(response) {
  if (typeof response.json !== 'function') return '';
  try {
    const payload = await response.json();
    return typeof payload?.detail === 'string' ? payload.detail : '';
  } catch (failure) {
    if (failure?.name === 'AbortError') throw failure;
    return '';
  }
}

export async function search(query, maxResults, signal) {
  const response = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, max_results: maxResults }),
    signal,
  });
  if (!response.ok) {
    const detail = await readErrorDetail(response);
    const message = response.status === 400
      ? 'Sprawdź zapytanie i spróbuj ponownie.'
      : 'Wyszukiwarka jest chwilowo niedostępna. Spróbuj ponownie za moment.';
    throw new UserFacingError(message, detail);
  }
  let data;
  try {
    data = await response.json();
  } catch (failure) {
    if (failure?.name === 'AbortError') throw failure;
    throw new UserFacingError('Nie udało się odczytać wyników wyszukiwania.');
  }
  if (!isValidResult(data)) throw new UserFacingError('Nie udało się odczytać wyników wyszukiwania.');
  return data;
}

export function safeUrl(value) {
  try {
    const url = new URL(value);
    return ['https:', 'http:'].includes(url.protocol) ? url : null;
  } catch { return null; }
}
