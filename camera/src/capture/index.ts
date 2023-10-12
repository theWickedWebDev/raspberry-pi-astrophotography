import { rejects } from 'assert';
import util from 'util';
const exec = util.promisify(require('child_process').exec);

export const PHOTO_CAPTURE_PATH = '/home/pi/captures';

export async function captureStack(count: number) {
    let counter = count || 1;

    return await new Promise(resolve => {
        const stackInterval = setInterval(async () => {
            console.log('capturing stack frame', counter);
            // try {
            //     const { stdout, stderr } = await exec(`
            //     gphoto2 \
            //         --filename "${PHOTO_CAPTURE_PATH}/%m-%d-%y/$NAME/ISO$ISO-f$APERTURE-${EXPOSURE}s-${FOCAL}mm-%m-%d-%y_%H:%M:%S.%C" \
            //         --set-config eosremoterelease=5 \
            //         --wait-event=${EXPOSURE}s \
            //         --set-config eosremoterelease=11 \
            //         --wait-event-and-download=2s
            //     `);

            //     if (stderr) console.error(stderr);
            // } catch (e) {
            //     console.error(e); // should contain code (exit code) and signal (that caused the termination).
            // }
            counter--;
            if (counter == 0) {
                clearInterval(stackInterval);
                console.log('Capture Complete')
                resolve('Capture Complete');
            }
        }, 1);
    });
}

export async function capture() {
    console.log('capturing')
}

export async function captureLights(config: { name: string, settings: any, frames: number, exposure: number, pathname?: string }) {
    const { name, settings, frames, exposure, pathname = PHOTO_CAPTURE_PATH } = config;

    let counter = frames || 1;
    const currentDate = new Date().toISOString().split('T')[0];

    return await new Promise((resolve, reject) => {
        const execCommand = `gphoto2 --filename "${PHOTO_CAPTURE_PATH}/${currentDate}/${name}/ISO${settings.iso}-f${settings.aperture}-${exposure}s-${settings.focalLength}mm-%m-%d-%y_%H:%M:%S.%C" --set-config eosremoterelease=5 --wait-event=${exposure}s --set-config eosremoterelease=11 --wait-event-and-download=3s`;
        const { stdout, stderr } = exec(execCommand);

        if (stderr) {
            console.error(stderr);
            reject(stderr);
        } else {
            console.log(stdout);
            resolve('Capture Complete');
        }

        // const stackInterval = setInterval(async () => {
        //     try {
        //         const { stdout, stderr } = await exec(`
        //             gphoto2 \
        //                 --filename "${pathname}/%m-%d-%y/${name}/ISO${settings.iso}-f${settings.aperture}-${exposure}s-${settings.focalLength}mm-%m-%d-%y_%H:%M:%S.%C" \
        //                 --set-config eosremoterelease=5 \
        //                 --wait-event=${exposure}s \
        //                 --set-config eosremoterelease=11 \
        //                 --wait-event-and-download=2s \
        //                 --hook-script /home/pi/astrophotography/camera/src/hooks/lights.sh
        //         `);

        //         if (stderr) console.error(stderr);
        //     } catch (e) {
        //         console.error(e); // should contain code (exit code) and signal (that caused the termination).
        //     }
        //     counter--;
        //     if (counter == 0) {
        //         clearInterval(stackInterval);
        //         console.log('Capture Complete')
        //         resolve('Capture Complete');
        //     }
        // }, 1);
    });

}

// async function captureDarks(count: number) {
//     // same settingd as lights
//     captureStack(count);
// }
// async function captureFlats(count: number) {
//     // Taken immediately after lights
//     captureStack(count);
// }

// async function captureBiases(count: number) {
//     // same as darks except 1/4000 shutter speed
//     captureStack(count);
// }




