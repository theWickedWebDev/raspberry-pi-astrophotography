
import prompts from 'prompts';
import yargs from 'yargs';
import Lenses from '../lenses';
prompts.override(yargs.argv);

type LensesType = typeof Lenses.KitLens_75_300mm | typeof Lenses.KitLens_18_55mm | typeof Lenses.Prime_50mm;

const promptForLens = async (): Promise<LensesType> => {
    let selectedLens: LensesType | undefined;

    while (!selectedLens) {
        const response = await prompts([
            {
                type: 'text',
                name: 'lens',
                message: `Which Lens are you using? \n  1. 18-55mm\n  2. 75-300mm\n  3. 50mm Prime`
            },
        ]);

        switch (response.lens) {
            case '1':
                selectedLens = Lenses.KitLens_18_55mm;
                break;
            case '2':
                selectedLens = Lenses.KitLens_75_300mm;
                break;
            case '3':
                selectedLens = Lenses.Prime_50mm;
                break;
            default:
                break;
        }
    }

    return selectedLens;
}

export default promptForLens;


