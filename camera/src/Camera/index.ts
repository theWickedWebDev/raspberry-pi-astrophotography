import { getCurrentConfigValue } from "../Gphoto2";

type CameraSettingOption = {
    current: string,
    options: string[]
};

type CameraSettings = {
    iso: CameraSettingOption;
    shutterspeed: CameraSettingOption;
    eosremoterelease: CameraSettingOption;
    reviewtime: CameraSettingOption;
    capturetarget: CameraSettingOption;
    imageformat: CameraSettingOption;
    whitebalance: CameraSettingOption;
    //
    artist: string;
    ownername: string;
    //
    shuttercounter?: number;
}

interface CameraType {
    settings: CameraSettings
};

class Camera {
    settings!: CameraSettings;

    constructor({ settings }: CameraType) {
        this.settings = settings;
    }

    async init() {
        const shuttercounter = await getCurrentConfigValue('shuttercounter');
        if (shuttercounter) this.settings.shuttercounter = parseInt(shuttercounter);
    }

    public setConfig(key: string, value: string) {
        console.log({ key, value }, ' config set');
    }

    public capture() {
        console.log('Capture image');
    }

    public getSettings() {
        return this.settings;
    }
}

export default Camera;