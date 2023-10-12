
import prompts, { Answers } from 'prompts';
import yargs from 'yargs';

prompts.override(yargs.argv);

const prompt = async (message: string): Promise<string | number> => {
    const response = await prompts([
        {
            type: 'text',
            name: 'prompt',
            message,
        },
    ]);

    return response.prompt;
}

export default prompt;