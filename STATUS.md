# STATUS.md

Aktualizacja: 2026-10-18.

- Wykonujemy audyt z docs/AUDYT-2026-10-17.md na docs/audyt-2026-10-17. Każdy etap kończy się testami, commitem i lokalnym merge do develop; następnie powrót na gałąź audytu. Bez push.
- Etapy kodu zakończone w tej sesji: S1, S2, Q1, S3, K3, S4, K1, K4, K2, S5. Ostatni: S5 — Nieuprzywilejowany proces i stały obraz.
- Dockerfile deklaruje USER 10001:10001. SearXNG przypięto do oficjalnego manifestu Docker Hub sha256:8bdd9aa136b2dc3b9332cf24714fa34a375b8a1949a1201ec900c24d7378596e (publiczne metadane 2026-10-18). Test konfiguracji PASS. Runtime UID/build niepotwierdzone: brak dostępu do docker.sock; nie uruchamiano sudo ani wdrożenia.
- Kontrole: backend 42/42, frontend 17/17, build i diff-check PASS. Testy offline; rzeczywistego wdrożenia nie potwierdzano.
- Otwarta czynność operatora S1: nowy SEARXNG_SECRET i start SearXNG; nie używać starej wartości z historii. Brak zgody na przepisywanie historii GitHuba.
- MCP nadal wymaga zgodnego kontraktu z wirralAI; punkty K1–K4 weryfikujemy na wspólnych przykładach.
