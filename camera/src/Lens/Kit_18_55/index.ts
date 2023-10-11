import Lens from "..";
import { settingsOptions } from './settings';

const KitLens = new Lens({
    name: 'EF-S18-55mm f/3.5-5.6 IS II',
    settings: {
        aperture: {
            current: settingsOptions.aperture[0],
            options: settingsOptions.aperture
        }
    }
});

export default KitLens;