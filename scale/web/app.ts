class App {
    private driver: ScaleDriver;
    private client: Client;

    // Variablen für die Waage
    private tareOffset: number = 0;
    private calibrationFactor: number = 0.0005; // Beispielwert: ADC-Units in KG umrechnen
    private isRunning: boolean = false;

    constructor(window: Window, document: Document, ip: string) {
        console.log("App starting...");

        this.client = new Client(ip, 5);

        const displayValue = document.getElementById('value');
        const displayRaw = document.getElementById('adc-raw');
        const btnTare = document.getElementById('btn-tare');
        const btnUpdate = document.getElementById('btn-update-settings');
        const inputCalib = <HTMLInputElement>document.getElementById('input-calib');
        const inputFreq = <HTMLInputElement>document.getElementById('input-freq');

        this.client.init(() => {
            console.log("Connected to Red Pitaya");
            this.driver = new ScaleDriver(this.client);

            this.updateSettings(inputFreq); // 100 kHz default
            this.isRunning = true;

            this.updateLoop(displayValue, displayRaw);
        });

        window.onbeforeunload = () => { this.client.exit(); };

        // Event Listener für Buttons
        btnTare.onclick = () => {
            this.performTare();
        };

        btnUpdate.onclick = () => {
            this.calibrationFactor = parseFloat(inputCalib.value);
            this.updateSettings(inputFreq);
        };
    }

    private updateSettings(inputFreq: HTMLInputElement) {
        const freq = parseFloat(inputFreq.value);
        this.driver.set_frequency(freq);
        console.log(`Frequenz gesetzt auf ${freq} Hz`);
    }

    // Aktuellen Wert als Nullpunkt speichern
    private performTare() {
        this.driver.get_adc_data((val) => {
            this.tareOffset = val;
            console.log(`Tara gesetzt. Offset: ${this.tareOffset}`);
        });
    }

    private updateLoop(displayEl: HTMLElement, debugEl: HTMLElement) {
        if (!this.isRunning) return;


        this.driver.get_adc_data((rawVal) => {
            
            // 1. Debug Anzeige (Rohwert)
            debugEl.innerText = rawVal.toString();

            let diff = rawVal - this.tareOffset;
            

            let weight = diff * this.calibrationFactor;


            displayEl.innerText = weight.toFixed(3);


            setTimeout(() => {
                this.updateLoop(displayEl, debugEl);
            }, 100); // 100ms Update Rate (10 Hz)
        });
    }
}

const app = new App(window, document, location.hostname);
