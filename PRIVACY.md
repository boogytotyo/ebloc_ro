# Politica de confidențialitate — e-Bloc Romania (integrare Home Assistant)

Această integrare este open-source și rulează **local** în instanța ta de Home Assistant. Nu operează niciun serviciu în cloud.

## Ce colectăm
Integrarea **nu colectează** și **nu transmite** date către autor. Totul rulează local.

## Ce stocăm
- **Cookie-urile e-bloc.ro** (ex. `PHPSESSID`, `asoc-cur`, `home-ap-cur`) sunt stocate în *config entry* Home Assistant pentru a putea interoga portalul.
- Preferințe locale (ex. perioada de istoric).

Aceste date rămân pe dispozitivul tău (serverul Home Assistant).

## Ce transmitem
- Cereri HTTPS către `e-bloc.ro` pentru a citi datele contului tău (facturi, index, istoric).
- Nu există telemetrie, analytics sau tracking extern.

## Controlul tău
- Poți șterge oricând integrarea din *Settings → Devices & services*; asta șterge și datele de configurare.
- Poți regenera/înlocui manual cookie-urile din UI/flow-ul de configurare.

## Securitate
- Home Assistant protejează fișierele de configurare și *secrets*. Recomandăm actualizări regulate și utilizarea HTTPS/ingress securizat.

## Contact
Întrebări? Deschide un *issue* pe GitHub: `https://github.com/boogytotyo/ebloc_ro/issues`.

Ultima actualizare: 26 Septembrie 2025
