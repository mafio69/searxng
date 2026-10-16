import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App.jsx';
import { HISTORY_KEY, PRIVATE_KEY, readHistory, remember } from './storage.js';

const response = { source: 'searxng', results: [{ title: 'Wynik testowy', url: 'https://example.org/test', snippet: 'Opis wyniku' }] };

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => response }));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

async function submit(query = 'Pomorze') {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText('Czego szukasz?'), query);
  await user.click(screen.getByRole('button', { name: 'Szukaj', exact: true }));
  return user;
}

describe('search application', () => {
  it('searches through the API, renders links and persists reusable history', async () => {
    render(<App />);
    const user = await submit();
    const link = await screen.findByRole('link', { name: /Wynik testowy/ });
    expect(link.getAttribute('href')).toBe('https://example.org/test');
    expect(fetch).toHaveBeenCalledWith('/api/search', expect.objectContaining({ body: JSON.stringify({ query: 'Pomorze', max_results: 10 }) }));
    expect(readHistory()[0].query).toBe('Pomorze');
    await user.click(screen.getByRole('button', { name: 'Pomorze', exact: true }));
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
    expect(readHistory()).toHaveLength(1);
  });

  it('does not save searches in private history mode, including after reload', async () => {
    render(<App />);
    const user = userEvent.setup();
    await user.click(screen.getByRole('checkbox', { name: /Bez zapisywania historii/ }));
    await submit('prywatne zapytanie');
    await screen.findByRole('link', { name: /Wynik testowy/ });
    expect(readHistory()).toEqual([]);
    expect(localStorage.getItem(PRIVATE_KEY)).toBe('true');
    cleanup(); render(<App />);
    expect(screen.getByRole('checkbox', { name: /Bez zapisywania historii/ }).checked).toBe(true);
  });

  it('restores history and supports removing one entry and clearing all with confirmation', async () => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify([{ query: 'A', time: 1 }, { query: 'B', time: 2 }]));
    render(<App />); const user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: 'Usuń z historii: A' }));
    expect(readHistory().map(item => item.query)).toEqual(['B']);
    await user.click(screen.getByRole('button', { name: /Wyczyść historię/ }));
    expect(readHistory()).toHaveLength(1);
    await user.click(screen.getByRole('button', { name: 'Usuń', exact: true }));
    expect(readHistory()).toEqual([]);
  });

  it('explains provider failure and offers retry', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ source: null, results: [] }) });
    render(<App />); const user = await submit();
    await screen.findByRole('alert');
    await user.click(screen.getByRole('button', { name: /Spróbuj ponownie/ }));
    await screen.findByRole('link', { name: /Wynik testowy/ });
  });

  it('handles empty results and hides unsafe result URLs', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ source: 'searxng', results: [{ title: 'unsafe', url: 'javascript:alert(1)' }] }) });
    render(<App />); await submit();
    await screen.findByText('Spróbuj spojrzeć inaczej');
    expect(screen.queryByRole('link', { name: 'unsafe' })).toBeNull();
  });

  it.each([null, { source: 'searxng', results: [null] },
    { source: 'searxng', results: [{ title: {}, url: 'https://example.org' }] },
    { source: 'unknown', results: [] }])('handles malformed API data without crashing: %j', async data => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => data });
    render(<App />); await submit();
    const alert = await screen.findByRole('alert');
    expect(alert.textContent).toContain('Nie udało się odczytać wyników wyszukiwania.');
    expect(screen.queryByRole('link', { name: /Wynik testowy/ })).toBeNull();
  });

  it('ignores a late response after returning to the start page', async () => {
    let resolve;
    fetch.mockReturnValueOnce(new Promise(done => { resolve = done; }));
    render(<App />);
    const user = await submit();
    await user.click(screen.getByRole('button', { name: 'Szukaj — strona główna' }));
    resolve({ ok: true, json: async () => response });
    await waitFor(() => expect(screen.queryByRole('status')).toBeNull());
    expect(screen.queryByRole('link', { name: /Wynik testowy/ })).toBeNull();
    expect(screen.getByText('Ciekawość to', { exact: false })).toBeTruthy();
  });

  it('handles network errors without leaving stale results', async () => {
    fetch.mockRejectedValueOnce(new Error('Brak połączenia'));
    render(<App />); await submit();
    await screen.findByRole('alert');
    expect(screen.queryByRole('link', { name: /Wynik testowy/ })).toBeNull();
  });
});

describe('history integrity', () => {
  it('preserves valid entries when another stored entry is null', () => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify([null, { query: 'valid', time: 1 }]));
    expect(readHistory()).toEqual([{ query: 'valid', time: 1 }]);
  });
  it('recovers from malformed storage and limits deduplicated history', () => {
    localStorage.setItem(HISTORY_KEY, '{broken'); expect(readHistory()).toEqual([]);
    localStorage.setItem(HISTORY_KEY, '{}'); expect(readHistory()).toEqual([]);
    let entries = [];
    for (let i = 0; i < 40; i++) entries = remember(entries, `query ${i}`, i);
    entries = remember(entries, 'QUERY 39', 50);
    expect(entries).toHaveLength(30);
    expect(entries[0]).toEqual({ query: 'QUERY 39', time: 50 });
  });
});
