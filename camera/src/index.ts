import { ExecOptions, exec } from "child_process";
import Camera from './Camera/Canon55d.camera';
import KitLens from './Lens/Kit_18_55';
import { getConfig, getCurrentConfigValue } from "./Gphoto2";

const run = async () => {
    // await Camera.init();
    console.log(await getConfig('whitebalance'));
    console.log(Camera);
    console.log(KitLens);
}

run();