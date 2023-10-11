export const allOptions = [
    'syncdatetime', 'uilock', 'popupflash',
    'autofocusdrive', 'manualfocusdrive', 'cancelautofocus',
    'eoszoom', 'eoszoomposition', 'viewfinder',
    'eosremoterelease', 'eosmoviemode', 'opcode',
    'datetime', 'reviewtime', 'output',
    'movierecordtarget', 'evfmode', 'ownername',
    'artist', 'copyright', 'customfuncex',
    'focusinfo', 'strobofiring', 'flashcharged',
    'autopoweroff', 'depthoffield', 'capturetarget',
    'capture', 'remotemode', 'eventmode',
    'serialnumber', 'manufacturer', 'cameramodel',
    'deviceversion', 'vendorextension', 'model',
    'ptpversion', 'Battery Level', 'batterylevel',
    'lensname', 'eosserialnumber', 'shuttercounter',
    'availableshots', 'eosmovieswitch', 'imageformat',
    'imageformatsd', 'iso', 'whitebalance',
    'whitebalancexa', 'whitebalancexb', 'colorspace',
    'exposurecompensation', 'focusmode', 'storageid',
    'autoexposuremode', 'drivemode', 'picturestyle',
    'aperture', 'shutterspeed', 'meteringmode',
    'liveviewsize', 'bracketmode', 'aeb',
    'alomode'
];

const iso = [
    'Auto', '100',
    '200', '400',
    '800', '1600',
    '3200', '6400'
];

const shutterspeed = [
    'bulb', '30', '25', '20', '15',
    '13', '10.3', '8', '6.3', '5',
    '4', '3.2', '2.5', '2', '1.6',
    '1.3', '1', '0.8', '0.6', '0.5',
    '0.4', '0.3', '1/4', '1/5', '1/6',
    '1/8', '1/10', '1/13', '1/15', '1/20',
    '1/25', '1/30', '1/40', '1/50', '1/60',
    '1/80', '1/100', '1/125', '1/160', '1/200',
    '1/250', '1/320', '1/400', '1/500', '1/640',
    '1/800', '1/1000', '1/1250', '1/1600', '1/2000',
    '1/2500', '1/3200', '1/4000'
]

const eosremoterelease = [
    'None', 'Press',
    'Press', 'Release',
    'Release', 'Immediate',
    'Press', 'Press',
    'Press', 'Release',
    'Release', 'Release'
];

const reviewtime = [
    'None', '2 seconds', '4 seconds', '8 seconds', 'Hold'
]

const capturetarget = ['Internal RAM', 'Memory card'];

const imageformat = [
    'Large Fine JPEG',
    'Large Normal JPEG',
    'Medium Fine JPEG',
    'Medium Normal JPEG',
    'Small Fine JPEG',
    'Small Normal JPEG',
    'RAW + Large Fine JPEG',
    'RAW',
];

const whitebalance = [
    'Auto',
    'Daylight',
    'Shadow',
    'Cloudy',
    'Tungsten',
    'Fluorescent',
    'Flash',
    'Manual'
];

const autoexposuremode = [
    'P',
    'TV',
    'AV',
    'Manual',
    'Bulb',
    'A_DEP',
    'DEP',
    'Custom',
    'Lock',
    'Green',
    'Night Portrait',
    'Sports',
    'Portrait',
    'Landscape',
    'Closeup',
    'Flash Off',
    'Auto',
    'Handheld Night Scene',
    'HDR Backlight Control',
    'Food',
    'Grainy B/W',
    'Soft focus',
    'Toy camera effect',
    'Fish-eye effect',
    'Water painting effect',
    'Miniature effect',
    'HDR art standard',
    'HDR art vivid',
    'HDR art bold',
    'HDR art embossed',
    'Panning',
    'Self Portrait',
    'Hybrid Auto',
    'Smooth skin',
    'Fv',
]
//

const ownername = 'Stephen Young';
const artist = 'Stephen Young';

export const settings = {
    iso,
    shutterspeed,
    eosremoterelease,
    reviewtime,
    capturetarget,
    imageformat,
    whitebalance,
    autoexposuremode,
    //
    ownername,
    artist
}