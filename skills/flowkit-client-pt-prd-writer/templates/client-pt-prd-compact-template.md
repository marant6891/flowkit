<!--
Szablon ZAPASOWY SKRÓCONY – dla małych zmian (SKILL.md, Etap 0: „Wariant dokumentu”).
Używaj go tylko, gdy użytkownik nie dostarczył własnego szablonu.
Cel: 1–3 strony. Sześć rozdziałów, bez rozdziałów „Nie dotyczy”. Tabela tylko dla wymagań
i tylko, gdy są co najmniej 3; pozostałe treści jako krótkie listy. Oznaczenia pochodzenia
(SRC/OPEN/ASSUMPTION) dopiskiem w nawiasie na końcu punktu.
Gdy w trakcie pracy okaże się, że zmiana dotyka integracji, migracji danych, uprawnień lub
architektury w stopniu wymagającym opisu – przejdź na szablon pełny i powiedz o tym użytkownikowi.
Usuń wszystkie komentarze i placeholdery [..] przed oddaniem dokumentu.
-->

# [Nazwa zmiany]

**Wersja:** [0.1] · **Data:** [DATA] · **Autor:** [AUTOR] · **Klient / system:** [KLIENT / SYSTEM] · **Status:** Roboczy

## 1. Cel i zakres

[2–4 zdania: co się zmienia, dlaczego i jaki efekt ma klient (SRC-001).]

- **W zakresie:** [element]; [element] (SRC-001)
- **Poza zakresem:** [element – dlaczego] (SRC-001)

## 2. Opis zmiany

- **Obecnie:** [jak działa dziś] (SRC-001)
- **Po zmianie:** [jak będzie działać] (SRC-001)

[Diagram procesu tylko, gdy proces ma rozgałęzienia lub kilku uczestników (Etap 5a).]

## 3. Wymagania

[1–2 wymagania: lista. Od 3 wymagań: tabela.]

- **FR-001** [Wymaganie]. Akceptacja: [sprawdzalne kryterium]. (SRC-001)

[Gdy zmiana jest widoczna dla użytkownika, kryterium zapisz jako jedną linię
Given-When-Then: „Mając [stan], gdy [akcja], wtedy [wynik].”]

## 4. Wpływ i ryzyka

- **Wpływ:** [moduł, ekran, raport, którego dotyczy zmiana] (SRC-002 / plik:linia)
- **Ryzyko:** [ryzyko ze źródła] – [działanie] (SRC-001)

[Brak dostępu do kodu: „Wpływu na kod nie analizowano – brak dostępu do repozytorium (OPEN-001).”]

## 5. Testy i odbiór

- [Scenariusz akceptacyjny] → [oczekiwany wynik] (FR-001)
- [Regresja: obszar do sprawdzenia] (SRC-002)
- **Gotowe, gdy:** [kryterium tej zmiany, np. scenariusze z rozdziału 3 zaliczone na środowisku testowym]

## 6. Tematy do wyjaśnienia

- **OPEN-001** [Czego brakuje] – wpływa na [FR/obszar]. Decyduje: [rola lub DO POTWIERDZENIA].
- **ASSUMPTION-001** [Założenie] – do potwierdzenia przez [rola].

[Brak tematów: „Brak otwartych tematów.”]

---

**Źródła:** SRC-001 [nazwa, data]; SRC-002 [nazwa, data]
