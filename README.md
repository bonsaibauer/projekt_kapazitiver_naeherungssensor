# Projekt 2: Kapazitiver Näherungssensor

## Projektübersicht
In diesem Projekt wird eine vollständige Sensorauswertung auf Basis des kapazitiven Messeffekts entwickelt. Das Projekt umfasst Sensorentwurf, analoge und digitale Signalauswertung sowie Visualisierung.

## Aufgabenstellung
### Sensorentwicklung
- Entwurf eines kapazitiven Sensors für einen frei wählbaren Anwendungsfall
- Mechanischer Aufbau
- Simulation mit Netgen/NGSolve
- Experimentelle Validierung

### Analoge Signalauswertung
- Brückenschaltung
- Instrumentenverstärker (z. B. INA111)
- Hochpassfilter zur Störunterdrückung

### Digitale Signalauswertung
- Datenerfassung mit Red Pitaya (Xilinx Zynq)
- Berechnung der Kapazitätsänderung
- Anzeige über LEDs und Webserver

## Technische Plattform
### Hardware
- Red Pitaya mit ADC/DAC (125 MS/s, 14 Bit)
- ARM Dual-Core + FPGA
- Ethernet

### Software
- Ubuntu Server (Koheron)
- FPGA-Logik
- C++/Python-Schnittstellen
- Webbasierte Visualisierung

## Bewertung
### Teil 1
- Sensor
- Simulation
- Signalerfassung

### Teil 2
- Signalauswertung
- Dokumentation

Besondere Gewichtung: Robustheit, Nachvollziehbarkeit, Analyse der Messabweichung.

## Abgabe
- Quellcode (Hardware + Software)
- Dokumentation (IEEE-Format)
- Präsentation

Abgabetermin: 19.03.2026