# Wkład w rozwój FlowKit (Contributing Guide)

Dziękujemy za zainteresowanie rozwojem biblioteki FlowKit! Poniżej znajdziesz wszystko, czego potrzebujesz, aby przygotować nowego skilla i zgłosić go przez Pull Request.

> [!IMPORTANT]
> Przed rozpoczęciem pracy zapoznaj się z dokumentem [**`DEVELOPMENT.md`**](DEVELOPMENT.md), który definiuje zasady inżynierskie, konwencję commitów oraz bezwzględną regułę wprowadzania zmian wyłącznie przez Pull Request (brak bezpośrednich pushy do `main`).

---

## 1. Wymagania dla nowego skilla

Każdy nowy skill musi spełniać poniższe wymagania, aby przejść walidację CI.

### Obowiązkowa struktura katalogów

```text
skills/<nazwa-skilla>/
├── SKILL.md             ← wymagany
├── CHANGELOG.md         ← wymagany
├── checklists/          ← wymagany (min. 1 plik .md)
├── templates/           ← wymagany (min. 1 plik .md)
├── examples/            ← zalecany
└── references/          ← zalecany
```

### Wymagany frontmatter SKILL.md

```yaml
---
name: nazwa-katalogu-skilla
version: "1.0"
tags: [tag1, tag2, tag3]
description: >
  Zwięzły opis (1–3 zdania): co robi skill, kiedy model AI powinien go aktywować
  i jaki jest format wyniku.
---
```

**Zasady:**
- `name` **musi być identyczne** z nazwą katalogu (`skills/<name>/`).
- Nazwa w formacie `kebab-case`, małe litery, bez polskich znaków.
- `tags` — co najmniej 3 słowa kluczowe po angielsku.
- `version` — format `"X.Y"` (np. `"1.0"`).

### Wymagana zawartość SKILL.md

Skill musi zawierać:
1. **Cel** — 2–4 zdania opisujące przeznaczenie.
2. **Zasady nadrzędne** — minimum 3, zawsze obowiązujące reguły (sprawdzalne obiektywnie).
3. **Etapy pracy** — minimum 3 etapy, ostatni musi być etapem weryfikacji z odesłaniem do checklisty.

### Zasada rzetelności (obowiązkowa we wszystkich skillach)

Każdy skill w FlowKit działa na zasadzie **„brak źródła = brak treści"**. Skill nigdy nie może zmyślać faktów, terminów, właścicieli ani wymagań. Brak danych oznacza się jako `[Do potwierdzenia]`, `OPEN-NNN` lub `Brak danych`.

---

## 2. Jak dodać nowego skilla krok po kroku

```bash
# 1. Sklonuj repozytorium i utwórz gałąź
git clone https://github.com/marant6891/flowkit.git
cd flowkit
git checkout -b feat/moj-nowy-skill

# 2. Skopiuj szablon skilla
cp -r skills/_template skills/moj-nowy-skill

# 3. Wypełnij SKILL.md i usuń komentarze szablonu
# 4. Dodaj szablony, checklists i przykłady
# 5. Dopisz skill do tabeli w README.md (odpowiednia kategoria)
# 6. Uruchom lokalną walidację
python scripts/validate_skills.py  # (jeśli dostępny) lub sprawdź ręcznie

# 7. Zatwierdź zmiany i otwórz PR
git add skills/moj-nowy-skill README.md
git commit -m "feat: add moj-nowy-skill"
git push origin feat/moj-nowy-skill
```

---

## 3. Standardy jakości (Code Review)

Pull Request zostanie odrzucony, jeśli:
- Skill zawiera zmyślone przykłady danych klientów, produktów lub dat.
- Frontmatter SKILL.md nie zawiera wymaganych pól lub `name` ≠ nazwa katalogu.
- Brak katalogu `templates/` z co najmniej jednym plikiem.
- Wewnętrzne linki w SKILL.md prowadzą do nieistniejących plików.
- W commicie znajdują się dane wrażliwe (tokeny, klucze API, hasła, nazwy klientów produkcyjnych).

---

## 4. Zgłaszanie pomysłów bez implementacji

Otwórz Issue używając szablonu **„Propozycja nowego skilla"** dostępnego w zakładce [Issues](../../issues/new/choose). Opisz scenariusz biznesowy, grupę docelową i oczekiwany format wyjścia.

---

## 5. Licencja

Wnosząc wkład, zgadzasz się, że Twój kod jest udostępniany na licencji [MIT](LICENSE).

