import util from 'util';
import { CameraConfigOptions } from './types';
const exec = util.promisify(require('child_process').exec);

const processResult = (stdout: string) => {
  const result = stdout.split('\n').filter(o => o.includes('Choice:')).map(o => o.split(' ')[2]);
  return result;
}

const processCurrentValueResult = (stdout: string) => {
  const result = stdout.split('\n').filter(o => o.includes('Current:')).map(o => o.split(' ')[1])[0];
  return result;
}

export async function getConfig(config: CameraConfigOptions) {
  try {
    const { stdout, stderr } = await exec(`gphoto2 --get-config ${config}`);

    return processResult(stdout);
    if (stderr) console.error(stderr);
  } catch (e) {
    console.error(e); // should contain code (exit code) and signal (that caused the termination).
  }
}

export async function getCurrentConfigValue(config: CameraConfigOptions) {
  try {
    const { stdout, stderr } = await exec(`gphoto2 --get-config ${config}`);

    return processCurrentValueResult(stdout);
    if (stderr) console.error(stderr);
  } catch (e) {
    console.error(e); // should contain code (exit code) and signal (that caused the termination).
  }
}