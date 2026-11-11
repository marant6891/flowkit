# Obsługiwane formaty transkrypcji spotkań

Różne platformy generują pliki `.vtt` z odmienną strukturą nagłówków i bloków czasu.
Poniżej wskazówki, jak je poprawnie przetwarzać.

---

## 1. Microsoft Teams (`.vtt`)

```text
WEBVTT

00:00:03.470 --> 00:00:06.730
<v Jan Kowalski>Dzień dobry, zaczynamy spotkanie.</v>

00:00:07.100 --> 00:00:12.000
<v Anna Nowak>Mam pytanie dotyczące zakresu wdrożenia.</v>
```

**Instrukcja:** Usuń nagłówek `WEBVTT`, znaczniki czasu (`HH:MM:SS.mmm --> HH:MM:SS.mmm`) oraz tagi HTML (`<v Imię Nazwisko>...</v>`). Wyodrębnij imię mówcy z tagu `<v ...>`.

---

## 2. Zoom (`.vtt`)

```text
WEBVTT

1
00:00:04.000 --> 00:00:08.500
Anna Nowak: Witam wszystkich, zacznijmy od agendy.

2
00:00:09.100 --> 00:00:14.200
Jan Kowalski: Chciałbym omówić termin dostarczenia makiet.
```

**Instrukcja:** Usuń nagłówek `WEBVTT`, numery sekwencji (cyfry samotne w linii), znaczniki czasu. Mówca jest wbudowany w treść (`Imię Nazwisko: treść`).

---

## 3. Google Meet (`.vtt` / transkrypcja `.docx`)

```text
WEBVTT

00:00:05.000 --> 00:00:09.000
Jan Kowalski: Proszę, żebyście przygotowali specyfikację do piątku.

00:00:10.000 --> 00:00:15.000
Anna Nowak: Możemy to zrobić do czwartku, jeśli dostaniemy dane dostępowe.
```

**Instrukcja:** Analogiczna do Zoom — brak numerów sekwencji, mówca wbudowany w treść.

---

## 4. Pliki `.docx` z automatyczną transkrypcją (Word, Teams)

Plik Word zawiera transkrypcję w tabeli lub jako ciągły tekst z nagłówkami mówców i znacznikami czasu w nawiasach, np. `[00:05:34]`. Usuń znaczniki czasu, zachowaj imiona mówców.

---

## Ogólne zasady filtrowania (wszystkie formaty)

- Usuń powtórzenia ASR (automatyczne rozpoznawanie mowy): frazy identyczne lub niemal identyczne w sąsiednich wierszach tego samego mówcy.
- Usuń dźwięki nieartykułowane transkrybowane jako słowa: `yyy`, `eee`, `mhm`, `okej okej`.
- Usuń komunikaty techniczne: `[Cisza]`, `[Muzyka]`, `[Niewyraźnie]`.
- Zachowaj pełne zdania merytoryczne nawet jeśli zawierają potoczny język — nie przeformułowuj treści, tylko ją ekstrahujesz.
