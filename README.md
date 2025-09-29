[![Release](https://img.shields.io/github/v/release/boogytotyo/ebloc_ro?display_name=tag&sort=semver)](https://github.com/boogytotyo/ebloc_ro/releases)
[![🚀 Release](https://github.com/boogytotyo/ebloc_ro/actions/workflows/release.yml/badge.svg)](https://github.com/boogytotyo/ebloc_ro/actions/workflows/release.yml)
[![Downloads](https://img.shields.io/github/downloads/boogytotyo/ebloc_ro/total.svg)](https://github.com/boogytotyo/ebloc_ro/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-blue.svg)](https://hacs.xyz/)
[![🧹 Lint](https://github.com/boogytotyo/ebloc_ro/actions/workflows/lint.yml/badge.svg)](https://github.com/boogytotyo/ebloc_ro/actions/workflows/lint.yml)
[![✅ Validate](https://github.com/boogytotyo/ebloc_ro/actions/workflows/validate.yml/badge.svg)](https://github.com/boogytotyo/ebloc_ro/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# e-Bloc Romania — Home Assistant custom integration

Integrare neoficială pentru [e-bloc.ro](https://www.e-bloc.ro) care aduce în Home Assistant:
- **senzori** pentru date utilizator, facturi restante, istoric facturi, index contor
- **entitatea de update** `update.ebloc_ro_update` pentru versiunea integrării

> Proiect open-source, fără afiliere la e-bloc.ro. Folosește sesiunea ta (cookie-uri) pentru a citi datele contului.

## Instalare

### Prin HACS (recomandat)
1. HACS → *Integrations* → ⋯ → *Custom repositories* → adaugă: `https://github.com/boogytotyo/ebloc_ro` (tip *Integration*).
2. Instalează **e-Bloc Romania** și repornește Home Assistant.
3. Settings → *Devices & services* → *Add integration* → **e-Bloc Romania**.

### Manual
Copiază folderul `custom_components/ebloc_ro` în `<config>/custom_components/` și repornește Home Assistant.

## Configurare
În onboarding, ți se vor cere:
- **Cookie-uri e-bloc.ro** (ex. `PHPSESSID`, `asoc-cur`, `home-ap-cur`), folosite doar local pentru a apela API-urile e-bloc.
- **History months** (opțional) — câte luni de istoric pentru indicii de contor.
- Exemplu cookie: `username=email%40email.com; PHPSESSID=xxx123yyyy456zzz789; home-ap-cur=123_45; home-stat-cur=6; avizier-luna-cur=-; facturi-luna-cur=-; index-luna-cur=-; asoc-cur=123`
<img width="1580" height="607" alt="image" src="https://github.com/user-attachments/assets/e910930a-848b-4eaf-92bf-0b9ad9dc4c66" />

## Entități expuse

### Senzori
- `sensor.ebloc_date_utilizator` — *eBloc Date Utilizator*
- `sensor.ebloc_factura_restanta` — *eBloc Factura Restanta*
- `sensor.ebloc_istoric_facturi` — *eBloc Istoric Facturi*
- `sensor.ebloc_index_contor` — *eBloc Index Contor*  
  **state**: ultimul index; **atribute**: perechi lună-an ↔ index pentru perioada configurată.

### Update
- `update.ebloc_ro_update` — notifică disponibilitatea unei versiuni noi a integrării și link către GitHub Releases.

## De ce cookie-uri?
e-bloc.ro nu oferă o API publică autentificată cu token; integrarea folosește o sesiune deja validă (aceleași cookie-uri din browserul tău) pentru a descărca datele contului tău. Cookie-urile sunt stocate criptat de Home Assistant în config entry și **nu părăsesc instanța ta**. Vezi [PRIVACY.md](PRIVACY.md).

## Depanare
- Dacă nu apar entitățile, verifică **logurile** (`home-assistant.log`) și re-autentifică în e-bloc.ro (cookie-urile pot expira).
- Pentru HACS, verifică cerințele de publicare/structură (manifest, README, `hacs.json`).
## Licență
[MIT](LICENSE)
