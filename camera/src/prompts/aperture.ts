
import prompts from 'prompts';
import yargs from 'yargs';

prompts.override(yargs.argv);

const promptForAperture = async (options: string[]): Promise<string> => {
    let aperture;

    while (!aperture) {
        const response = await prompts([
            {
                type: 'text',
                name: 'aperture',
                message: `Aperture:\n${options.sort((a, b) => parseInt(a) - parseInt(b)).map((a, i) => `  ${i}) ƒ/${a}\n`).join('')}`
            },
        ]);

        if (!!options[response.aperture]) {
            aperture = options[response.aperture];
        }
    }

    return aperture;
}

export default promptForAperture;