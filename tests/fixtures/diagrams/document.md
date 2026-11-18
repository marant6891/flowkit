# Dokument PT: ACME

Oznaczenia: SRC-001, SRC-002, SRC-003, SRC-004, OPEN-001, OPEN-002.

## 2. Architektura rozwiązania

Platforma ACME obejmuje Portal klienta, Usługa zamówień i Baza zamówień. Portal odpowiada za składanie zamówień. Usługa wykonuje zapis i odczyt danych oraz przekazanie zamówienia do komponentu System ERP.

### Odpowiedzialności komponentów

Opis szczegółowy.

## 3. Proces reklamacji

Kroki: Zgłoszenie reklamacji, Weryfikacja reklamacji, Czy uznana?, Zwrot środków, Wysłanie odmowy, Zamknięcie sprawy.

Akceptacja: Złożenie zamówienia, Akceptacja zamówienia, Rejestracja zamówienia. Role: Klient, Konsultant, System ERP.

## 4. Integracje

Portal klienta, Usługa zamówień i System ERP wymieniają dane: złożenie zamówienia, walidacja danych, przekazanie zamówienia, numer zamówienia i potwierdzenie.

## 5. Model danych

Encje: Klient, Zamówienie, Pozycja zamówienia. Atrybuty: id, email, klient_id, zamowienie_id, status, ilosc; typy: tekst i liczba.

## 6. Bezpieczeństwo

Role: Konsultant, Administrator. Zasoby: Zamówienia, Raporty. Uprawnienia: odczyt i edycja.

## 7. Wdrożenie

Etapy: Analiza (styczeń 2027), Implementacja (luty 2027), Testy akceptacyjne (marzec 2027), Uruchomienie.
