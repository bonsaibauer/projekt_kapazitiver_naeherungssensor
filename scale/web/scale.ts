class ScaleDriver {
    private driver: Driver;
    private id: number;
    private cmds: HashTable<ICommand>;

    constructor(private client: Client) {
        this.driver = this.client.getDriver('ScaleDriver');
        this.id = this.driver.id;
        this.cmds = this.driver.getCmds();
    }

    set_frequency(frequencyHz: number): void {
        this.client.send(Command(this.id, this.cmds['set_frequency'], frequencyHz));
    }

    get_adc_data(cb: (value: number) => void): void {
        this.client.readUint32(
            Command(this.id, this.cmds['get_adc_data']),
            (value) => { cb(value); }
        );
    }

    set_leds(value: number): void {
        this.client.send(Command(this.id, this.cmds['set_leds'], value));
    }
}
