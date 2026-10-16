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
  if (!data || !['searxng', 'perplexity-fast', null].includes(data.source) ||
      !Array.isArray(data.results) || data.results.some(item =>
        !item || typeof item !== 'object' || Array.isArray(item) ||
        ['title', 'url', 'snippet'].some(field => item[field] != null && typeof item[field] !== 'string'))) throw new Error('Nie udało się odczytać wyników wyszukiwania.');
  return data;
}

export function safeUrl(value) {
  try {
    const url = new URL(value);
    return ['https:', 'http:'].includes(url.protocol) ? url : null;
  } catch { return null; }
}
