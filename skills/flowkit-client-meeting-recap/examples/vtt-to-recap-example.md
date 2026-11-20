# Przykład: od surowego VTT do dwóch plików podsumowania

Dane fikcyjne. Spotkanie odbyło się w poniedziałek 09.11.2026 (data podana przez użytkownika).

## 1. Surowy fragment transkrypcji (.vtt z MS Teams)

```text
WEBVTT

00:15:32.400 --> 00:15:36.200
<v Jan Kowalski>Czy jesteście w stanie przygotować te makiety do środy? Bo w czwartek mam zarząd.</v>

00:15:36.500 --> 00:15:40.100
<v Anna Nowak>Do środy damy radę z wersją dla ścieżki głównej. Panel admina zostawimy na kolejny tydzień.</v>

00:15:40.300 --> 00:15:44.200
<v Jan Kowalski>Dobra, to mi wystarczy na zarząd. Ja w zamian podeślę wam specyfikację API płatności najpóźniej do wtorku rano.</v>

00:15:44.800 --> 00:15:48.000
<v Piotr Wiśniewski>Cześć, przepraszam, przerwało mi połączenie, o czym mówimy?</v>

00:16:02.100 --> 00:16:09.700
<v Jan Kowalski>A, i fajnie byłoby kiedyś dorobić do tego aplikację na zegarki. Ale to luźna myśl.</v>

00:16:10.200 --> 00:16:13.000
<v Anna Nowak>Zapiszę to sobie, wrócimy do tematu.</v>
```

Role podane przez użytkownika: Jan Kowalski — klient; Anna Nowak — analityk w naszym zespole.
Rola Piotra Wiśniewskiego nie wynika z materiałów.

---

## 2. Plik `recap-2026-11-09-platnosci-wewnetrzne.md` (Część A)

| Obszar | Dowód z transkrypcji (cytat, mówca, czas) | Interpretacja |
|---|---|---|
| Nastroje klienta / dynamika rozmowy | „Bo w czwartek mam zarząd.” — Jan Kowalski, 00:15:32 | Interpretacja: presja terminu po stronie klienta; środowy termin makiet jest dla niego krytyczny. |
| Próby rozszerzenia zakresu (Scope Creep) | „fajnie byłoby kiedyś dorobić do tego aplikację na zegarki. Ale to luźna myśl.” — Jan Kowalski, 00:16:02 | Interpretacja: pomysł poza zakresem, bez zobowiązania żadnej ze stron. Nie trafia do maila. |
| Zależności i wąskie gardła | „podeślę wam specyfikację API płatności najpóźniej do wtorku rano” — Jan Kowalski, 00:15:40 | Interpretacja: dalsze prace zależą od dostawy po stronie klienta. |

Punkty uwagi: rola Piotra Wiśniewskiego — `DO POTWIERDZENIA`.

---

## 3. Plik `recap-2026-11-09-platnosci-klient.md` (Część B, fragment)

### 1. Kluczowe decyzje i ustalenia merytoryczne

- **Zakres makiet na zarząd:** Do środy 11.11.2026 przygotujemy makiety głównej ścieżki użytkownika. Makiety panelu administracyjnego powstaną w kolejnym tygodniu.

### 2. Kolejne kroki i zadania (Action Items)

#### Po stronie naszego zespołu:

| Zadanie | Osoba odpowiedzialna | Termin realizacji |
|---|---|---|
| Przygotowanie makiet głównej ścieżki użytkownika | Anna Nowak | 11.11.2026 |
| Przygotowanie makiet panelu administracyjnego | DO POTWIERDZENIA | DO POTWIERDZENIA |

#### Po stronie Klienta:

| Zadanie | Osoba odpowiedzialna | Termin realizacji |
|---|---|---|
| Przekazanie specyfikacji API płatności | Jan Kowalski | 10.11.2026 (rano) |

### 4. Następne kroki i weryfikacja ustaleń

- **Kolejne spotkanie:** DO POTWIERDZENIA.
- **Weryfikacja ustaleń:** *Gdyby którykolwiek z powyższych punktów różnił się od Państwa notatek lub wymagał doprecyzowania, uprzejmie proszę o informację zwrotną w ciągu 48 godzin.*

---

## 4. Dlaczego tak

- **Daty:** „do środy” i „do wtorku rano” przeliczono na daty, bo znana jest data spotkania. Bez niej zostałoby brzmienie z transkrypcji.
- **Panel admina:** „kolejny tydzień” to nie konkretny termin, a właściciel nie padł — stąd `DO POTWIERDZENIA`, bez zgadywania.
- **Aplikacja na zegarki:** luźny pomysł bez zgody obu stron — tylko w Części A.
- **Wtrącenie Piotra Wiśniewskiego:** szum techniczny, pominięty w obu częściach.
