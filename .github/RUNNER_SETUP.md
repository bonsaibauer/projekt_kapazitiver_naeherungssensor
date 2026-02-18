# Koheron Self-Hosted Runner

Der Workflow fuer das deploybare `scale.zip` benoetigt einen Self-Hosted Runner mit Labeln:

- `self-hosted`
- `linux`
- `x64`
- `koheron`

## Einrichtung

1. In GitHub: `Settings -> Actions -> Runners -> New self-hosted runner`.
2. Linux x64 waehlen.
3. Runner auf dem Build-Rechner installieren und registrieren.
4. Beim Registrieren das Label `koheron` setzen.
5. Runner-Service starten.

## Erforderliche Umgebung

- Zugriff auf das `koheron-sdk` Repo
- Koheron Build-Toolchain (Vivado + Build-Abhaengigkeiten)
- `make`, `python3`, `zip`, `unzip`, `docker` (falls genutzt)

## Workflow-Konfiguration

- Variable `KOHERON_SDK_REPOSITORY` optional setzen (Default: `Koheron/koheron-sdk`)
- Secret `KOHERON_SDK_PAT` setzen, wenn SDK-Repo privat ist
