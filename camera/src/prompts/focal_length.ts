
import prompts from 'prompts';
import yargs from 'yargs';
import Lenses from '../lenses';
prompts.override(yargs.argv);

type LensesType = typeof Lenses.KitLens_18_55mm | typeof Lenses.KitLens_18_55mm | typeof Lenses.Prime_50mm;

const promptForFocalLength = async (selectedLens: LensesType): Promise<keyof typeof selectedLens.focalLengths> => {
    let focalLength: keyof typeof selectedLens.focalLengths | undefined;

    while (!focalLength) {
        const focalLengths = Object.keys(selectedLens.focalLengths);

        const response = await prompts([
            {
                type: 'text',
                name: 'focalLength',
                message: `What focal length is it set to?\n${focalLengths.map(fl => `  ${fl}: ${fl}mm\n`).join('')}`
            },
        ]);

        // @ts-ignore
        if (selectedLens.focalLengths[response.focalLength]) {
            focalLength = response.focalLength;
        }
    }

    return focalLength;
}

export default promptForFocalLength;