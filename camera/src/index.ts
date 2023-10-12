import util from 'util';
import prompts from 'prompts';
import * as settings from './constants';
import { PHOTO_CAPTURE_PATH, captureLights } from './capture';
import yargs from 'yargs';
import promptForFocalLength from './prompts/focal_length';
import promptForLens from './prompts/lens';
import promptForAperture from './prompts/aperture'
import promptForISO from './prompts/iso';
import prompt from './prompts/prompt';

const exec = util.promisify(require('child_process').exec);

prompts.override(yargs.argv);

const DEFAULT_CAMERA_SETTINGS: object = {
    shutterspeed: settings.shutterspeed['bulb'],
    eosremoterelease: settings.REMOTE_RELEASE_NONE,
    reviewtime: settings.REVIEWTIME_NONE,
    capturetarget: settings.CAPTURE_TARGET_RAM,
    imageformat: settings.IMAGE_FORMAT_RAW_AND_JPEG,
    whitebalance: settings.WHITEBALANCE_DAYLIGHT,
    autoexposuremode: settings.EXPOSURE_MODE_MANUAL,
    drivemode: settings.DRIVEMODE_SINGLE,
    picturestyle: settings.PICTURESTYLE_LANDSCAPE,

    // Static
    artist: settings.ARTIST,
    ownername: settings.OWNERNAME,
};

//
//
//
//

let selectedLens, focalLength, iso, aperture;

const setupCamera = async () => {
    const gphotoConfig = Object.entries(DEFAULT_CAMERA_SETTINGS).map(([k, v]) => `--set-config-value ${k}="${v}"`).join(' ');
    const { stdout, stderr } = await exec(`gphoto2 ${gphotoConfig}`);
}

const run = async () => {
    // TODO: Save last settings to file?

    // Prompt for capture action
    // Stacks: 1. Lights / Flats / Biases / Darks
    // Single: 
    let cameraSettings: object = {};

    let confirmation = false;
    while (!confirmation) {
        selectedLens = await promptForLens();
        // TODO
        // @ts-ignore
        focalLength = await promptForFocalLength(selectedLens);
        iso = await promptForISO();
        aperture = await promptForAperture(Object.keys(selectedLens.focalLengths[focalLength]));

        cameraSettings = {
            ...cameraSettings,
            iso,
            aperture,
            lens: selectedLens.name,
            focalLength,
        };

        Object.entries(cameraSettings).map(s => console.log(`${s[0]}: ${s[1]}`));
        const confirmationResponse = await prompt("Settings look good [Enter to accept] or [0 | n | No to change]");
        if (![0, 'N', 'n', 'no', 'No'].includes(confirmationResponse)) {
            confirmation = true;
        }
    }

    const captureDirectory = await prompt(`Where should images be downloaded? [default: ${PHOTO_CAPTURE_PATH}[Enter for default]`) as string;
    const shootName = await prompt(`Target Object or name for photoshoot:`) as string;
    const frames = await prompt(`Number of frames to shoot: [Default: 1]`) as string;
    const exposureTime = await prompt(`Exposure time: [Default: 1]`) as string;

    try {
        await captureLights({
            name: shootName,
            settings: cameraSettings,
            frames: parseInt(frames) || 1,
            exposure: parseInt(exposureTime) || 1,
            pathname: captureDirectory
        });

    } catch (e) {
        console.error(e);
    }
}

const init = async () => {
    await setupCamera();
    await run();
}

init();
