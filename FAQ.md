# FAQ — e-Bloc Romania

**De ce trebuie să introduc cookie-uri?**  
Autentificarea la e-bloc.ro se face prin sesiune. Integrarea folosește cookie-urile tale (ex. `PHPSESSID`, `asoc-cur`, `home-ap-cur`) pentru a reproduce acea sesiune și a descărca datele contului.

**Unde sunt stocate cookie-urile?**  
În Home Assistant, ca parte din *config entry*. Sunt păstrate local pe instanța ta, nu sunt trimise către alte servere.

**Ce se întâmplă dacă expiră sesiunea?**  
Senzorii vor eșua la refresh. Re-deschide integrarea și lipește cookie-urile actualizate din browserul tău.

**Pot să am mai multe asociații/locații?**  
Da, dacă sesiunea ta le vede în portal, integrarea poate colecta datele aferente. Dacă vrei instanțe separate, adaugă integrarea de mai multe ori cu sesiuni/cookie-uri diferite.

**De ce nu se vede tot istoricul la `sensor.ebloc_index_contor`?**  
Câmpul `history months` din configurare controlează câte luni sunt cerute. Crește valoarea și reîncarcă integrarea.

**Ce date trimite integrarea în exterior?**  
Doar solicitări HTTPS către `e-bloc.ro` pentru a citi datele tale. Nu există telemetrie. Vezi [PRIVACY.md](PRIVACY.md).

**Cum raportez o problemă sau propun o îmbunătățire?**  
Deschide un *issue* pe GitHub: `https://github.com/boogytotyo/ebloc_ro/issues`.
