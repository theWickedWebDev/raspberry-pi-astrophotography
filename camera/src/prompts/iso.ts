
import prompts from 'prompts';
import yargs from 'yargs';
import { ISO_VALUES } from '../constants';
prompts.override(yargs.argv);

const promptForISO = async (): Promise<string> => {
    let iso: string | undefined;

    while (!iso) {

        const response = await prompts([
            {
                type: 'text',
                name: 'iso',
                message: `ISO\n${ISO_VALUES.map((_iso, i) => `  ${i}: ISO${_iso}\n`).join('')}`
            },
        ]);

        // @ts-ignore
        if (ISO_VALUES[response.iso]) {
            iso = ISO_VALUES[response.iso];
        }
    }

    return iso;
}

export default promptForISO;