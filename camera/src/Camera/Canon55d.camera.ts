import _Camera from ".";
import { settings } from "./550D/settings";

const Camera = new _Camera({
    settings: {
        iso: {
            current: '100',
            options: settings.iso
        },
        shutterspeed: {
            current: 'bulb',
            options: settings.shutterspeed
        },
        eosremoterelease: {
            current: settings.eosremoterelease[0],
            options: settings.eosremoterelease
        },
        reviewtime: {
            current: settings.reviewtime[0],
            options: settings.reviewtime
        },
        capturetarget: {
            current: settings.capturetarget[0],
            options: settings.capturetarget
        },
        imageformat: {
            current: settings.imageformat[7],
            options: settings.imageformat
        },
        whitebalance: {
            current: settings.whitebalance[1],
            options: settings.whitebalance
        },
        //
        artist: settings.artist,
        ownername: settings.ownername,
    }
});


export default Camera;