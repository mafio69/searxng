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

export async function search(query, maxResults, signal) {
  const response = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, max_results: maxResults }),
    signal,
  });
  if (!response.ok) throw new Error(response.status === 400
    ? 'Sprawdź zapytanie i spróbuj ponownie.'
    : 'Wyszukiwarka jest chwilowo niedostępna. Spróbuj ponownie za moment.');
  const data = await response.json();
  if (!isValidResult(data)) throw new Error('Nie udało się odczytać wyników wyszukiwania.');
  return data;
}

export function safeUrl(value) {
  try {
    const url = new URL(value);
    return ['https:', 'http:'].includes(url.protocol) ? url : null;
  } catch { return null; }
}
