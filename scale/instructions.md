# Digitale Kapazitive Waage (Red Pitaya / Koheron)

## Wichtig: Wann `make` notwendig ist

`make` passiert **nicht** beim Klick auf "Add instrument" im Koheron-Webtool.

Das Webtool installiert nur ein bereits fertiges Instrument-ZIP.  
Das fertige ZIP muss vorher gebaut werden.

## Korrekte Reihenfolge

1. Instrument lokal mit Koheron SDK bauen (`make`).
2. Das erzeugte `scale.zip` hochladen.
3. Im Koheron-UI "Run" wählen.
4. Webinterface unter `http://<red-pitaya-ip>/` aufrufen.

## Lokaler Build (empfohlen)

Beispiel (Linux/WSL, im `koheron-sdk`):

```bash
make CONFIG=/pfad/zu/projekt_kapazitiver_naeherungssensor/scale/config.yml
```

Das ZIP liegt danach unter `koheron-sdk/tmp/.../scale.zip`.

Optional direkt aufs Board:

```bash
export HOST=192.168.8.193
make CONFIG=/pfad/zu/projekt_kapazitiver_naeherungssensor/scale/config.yml run
```

## Upload im Koheron-Webtool

1. `http://<red-pitaya-ip>/koheron` öffnen.
2. "Add instrument" klicken.
3. Das mit `make` erzeugte `scale.zip` auswählen.
4. "Run" beim Instrument `scale`.
5. Danach `http://<red-pitaya-ip>/` öffnen.

## Hinweis

Der Build des deploybaren Instrument-ZIPs erfolgt lokal mit Koheron `make`.
