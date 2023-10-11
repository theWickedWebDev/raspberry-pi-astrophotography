type LensSettings = {
    aperture: {
        current: string,
        options: string[]
    }
}

interface LensType {
    name: string;
    settings: LensSettings
}

class Lens {
    name!: string;
    settings!: LensSettings;

    constructor({ name, settings }: LensType) {
        this.name = name;
        this.settings = settings;
    }
}

export default Lens;