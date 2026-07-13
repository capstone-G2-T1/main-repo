// ─── Types ───────────────────────────────────────────────────────────────────

export interface Brand {
  id: string;
  name: string;
  nameAr: string;
  hex: string;
  gradient: string;
  desc: string;
  descAr: string;
  logo: string;
}

export interface VehicleSpecs {
  length: string;
  width: string;
  height: string;
  wheelbase: string;
  weight: string;
  drivetrain: string;
}

export interface Vehicle {
  id: string;
  brand: string;
  name: string;
  nameAr: string;
  year: number;
  type: string;
  typeAr: string;
  range: number | null;
  battery: string;
  power: string;
  accel: string;
  maxSpeed: number;
  seats: number;
  price: string;
  priceAr: string;
  image: string;
  specs: VehicleSpecs;
  features: string[];
  featuresAr: string[];
}

// ─── Brands ──────────────────────────────────────────────────────────────────

export const BRANDS: Brand[] = [
  {
    id: 'byd', name: 'BYD', nameAr: 'بي واي دي', hex: '#1060CC',
    gradient: 'linear-gradient(135deg,#001a40,#0055cc)',
    desc: 'World leader in new energy vehicles',
    descAr: 'الرائد العالمي في مركبات الطاقة الجديدة',
    logo: '/images/logos/byd.webp',
  },
  {
    id: 'gac', name: 'GAC', nameAr: 'جي إيه سي', hex: '#C0392B',
    gradient: 'linear-gradient(135deg,#2c0a0a,#8b0000)',
    desc: 'Guangzhou Automobile Group Co.',
    descAr: 'مجموعة غوانغتشو للسيارات',
    logo: '/images/logos/gac.png',
  },
  {
    id: 'geely', name: 'Geely', nameAr: 'جيلي', hex: '#1A5276',
    gradient: 'linear-gradient(135deg,#0a1929,#1a5276)',
    desc: 'Smart mobility, global reach',
    descAr: 'التنقل الذكي بامتداد عالمي',
    logo: '/images/logos/geely.jpg',
  },
  {
    id: 'haval', name: 'Haval', nameAr: 'هافال', hex: '#922B21',
    gradient: 'linear-gradient(135deg,#1a0a0a,#7b241c)',
    desc: 'The global SUV specialist',
    descAr: 'متخصص السيارات الدفع الرباعي عالمياً',
    logo: '/images/logos/haval.png',
  },
  {
    id: 'mg', name: 'MG', nameAr: 'إم جي', hex: '#96281B',
    gradient: 'linear-gradient(135deg,#1a0505,#96281b)',
    desc: 'British heritage. Future tech.',
    descAr: 'تراث بريطاني. تقنية المستقبل.',
    logo: '/images/logos/mg.png',
  },
  {
    id: 'ora', name: 'ORA', nameAr: 'أورا', hex: '#6C3483',
    gradient: 'linear-gradient(135deg,#0d0d1a,#4a235a)',
    desc: 'Futuristic EVs, adorably designed',
    descAr: 'سيارات كهربائية مستقبلية بتصميم ساحر',
    logo: '/images/logos/ora.jpg',
  },
  {
    id: 'vw', name: 'Volkswagen', nameAr: 'فولكس واجن', hex: '#1A3A5C',
    gradient: 'linear-gradient(135deg,#050e1a,#1a3a5c)',
    desc: 'German precision. Electric future.',
    descAr: 'دقة ألمانية. مستقبل كهربائي.',
    logo: '/images/logos/vw.png',
  },
];

// ─── Vehicles ─────────────────────────────────────────────────────────────────

export const VEHICLES: Vehicle[] = [
  // ── BYD ──────────────────────────────────────────────────────────────────
  {
    id: 'byd-dolphin', brand: 'byd', name: 'Dolphin 2025', nameAr: 'دولفين 2025',
    year: 2025, type: 'Electric Hatchback', typeAr: 'هاتشباك كهربائي',
    range: 340, battery: '44.9 kWh', power: '130 kW', accel: '7.0s',
    maxSpeed: 160, seats: 5, price: 'From $19,000', priceAr: 'من $19,000',
    image: '/images/vehicles/dolphin.png',
    specs: { length:'4290mm', width:'1770mm', height:'1570mm', wheelbase:'2700mm', weight:'1405 kg', drivetrain:'FWD' },
    features: ['BladeGuard Battery','DiLink 3.0','V2L Charging','Dual Climate Zones','Rotating Center Console'],
    featuresAr: ['بطارية BladeGuard','DiLink 3.0','شحن خارجي V2L','تكييف منطقتين','كونسول مركزي دوار'],
  },
  {
    id: 'byd-seagull', brand: 'byd', name: 'Seagull', nameAr: 'سيغل',
    year: 2024, type: 'Electric Mini', typeAr: 'ميني كهربائي',
    range: 405, battery: '38.88 kWh', power: '55 kW', accel: '10.9s',
    maxSpeed: 130, seats: 5, price: 'From $11,000', priceAr: 'من $11,000',
    image: '/images/vehicles/BYD_SEAGULL.png',
    specs: { length:'3780mm', width:'1715mm', height:'1540mm', wheelbase:'2500mm', weight:'1285 kg', drivetrain:'FWD' },
    features: ['Blade Battery','30-min Fast Charge','Smart Cockpit','Advanced ADAS','City EV Design'],
    featuresAr: ['بطارية Blade','شحن 30 دقيقة','كوكبيت ذكي','ADAS متقدم','تصميم مدني'],
  },
  {
    id: 'byd-seal', brand: 'byd', name: 'Seal 2025', nameAr: 'سيل 2025',
    year: 2025, type: 'Electric Sedan', typeAr: 'سيدان كهربائي',
    range: 700, battery: '82.56 kWh', power: '390 kW', accel: '3.8s',
    maxSpeed: 180, seats: 5, price: 'From $29,000', priceAr: 'من $29,000',
    image: '/images/vehicles/seal.png',
    specs: { length:'4800mm', width:'1875mm', height:'1460mm', wheelbase:'2920mm', weight:'2055 kg', drivetrain:'AWD' },
    features: ['Dual Motor AWD','Cell-to-Body (CTB)','iTAC Traction','DiPilot Autonomous','OTA Updates'],
    featuresAr: ['دفع رباعي','تقنية CTB','iTAC للجر','DiPilot','تحديثات هوائية'],
  },
  {
    id: 'byd-sealion7', brand: 'byd', name: 'Sealion 7', nameAr: 'سيليون 7',
    year: 2024, type: 'Electric SUV', typeAr: 'إس يو في كهربائي',
    range: 502, battery: '71.8 kWh', power: '390 kW', accel: '4.5s',
    maxSpeed: 215, seats: 5, price: 'From $34,000', priceAr: 'من $34,000',
    image: '/images/vehicles/BYD_SEALION_7.png',
    specs: { length:'4830mm', width:'1925mm', height:'1620mm', wheelbase:'2930mm', weight:'2185 kg', drivetrain:'AWD' },
    features: ['800V Ultra-Fast Charge','Panoramic Roof','HUD Display','Air Suspension','AWD Performance'],
    featuresAr: ['شحن 800V','سقف بانورامي','HUD','تعليق هوائي','أداء AWD'],
  },
  {
    id: 'byd-song-plus', brand: 'byd', name: 'Song Plus DM-i', nameAr: 'سونغ بلاس DM-i',
    year: 2024, type: 'Plug-in Hybrid SUV', typeAr: 'هجين قابل للشحن',
    range: 1200, battery: '18.3 kWh', power: '138 kW', accel: '6.9s',
    maxSpeed: 180, seats: 5, price: 'From $24,000', priceAr: 'من $24,000',
    image: '/images/vehicles/BYD_SONG_PLUS_DM.png',
    specs: { length:'4710mm', width:'1890mm', height:'1680mm', wheelbase:'2712mm', weight:'1905 kg', drivetrain:'FWD' },
    features: ['EV Range 80km','DM-i Super Hybrid','DiLink 4.0','Smart Thermal Mgmt','Wireless CarPlay'],
    featuresAr: ['مدى EV 80كم','هجين DM-i','DiLink 4.0','تبريد ذكي','CarPlay لاسلكي'],
  },
  // ── GAC ──────────────────────────────────────────────────────────────────
  {
    id: 'gac-empow', brand: 'gac', name: 'Empow', nameAr: 'إمبو',
    year: 2023, type: 'Sports Sedan', typeAr: 'سيدان رياضي',
    range: null, battery: '2.0T Engine', power: '165 kW', accel: '6.5s',
    maxSpeed: 220, seats: 5, price: 'From $22,000', priceAr: 'من $22,000',
    image: '/images/vehicles/gacempow2021.png',
    specs: { length:'4685mm', width:'1857mm', height:'1465mm', wheelbase:'2778mm', weight:'1520 kg', drivetrain:'FWD' },
    features: ['2.0T Turbocharged','Sport Mode','LED Matrix Headlights','Virtual Cockpit','10.25" Screen'],
    featuresAr: ['محرك 2.0T','وضع رياضي','مصابيح LED','كوكبيت افتراضي','شاشة 10.25"'],
  },
  {
    id: 'gac-gs3', brand: 'gac', name: 'GS3 Emzoom', nameAr: 'GS3 إيمزوم',
    year: 2023, type: 'Compact SUV', typeAr: 'إس يو في مدمج',
    range: null, battery: '1.5T Engine', power: '124 kW', accel: '8.9s',
    maxSpeed: 180, seats: 5, price: 'From $18,000', priceAr: 'من $18,000',
    image: '/images/vehicles/GAC_GS3_EMZOOM.png',
    specs: { length:'4455mm', width:'1856mm', height:'1650mm', wheelbase:'2650mm', weight:'1480 kg', drivetrain:'FWD' },
    features: ['Panoramic Sunroof','Lane Keep Assist','Auto Parking','12.3" Cluster','Wireless CarPlay'],
    featuresAr: ['سقف بانورامي','مساعد مسار','ركن تلقائي','عداد 12.3"','CarPlay لاسلكي'],
  },
  {
    id: 'gac-gs4', brand: 'gac', name: 'GS4', nameAr: 'GS4',
    year: 2023, type: 'Mid-size SUV', typeAr: 'إس يو في متوسط',
    range: null, battery: '1.5T Engine', power: '133 kW', accel: '8.5s',
    maxSpeed: 185, seats: 5, price: 'From $21,000', priceAr: 'من $21,000',
    image: '/images/vehicles/GAC_GS4.png',
    specs: { length:'4550mm', width:'1856mm', height:'1698mm', wheelbase:'2680mm', weight:'1530 kg', drivetrain:'FWD/AWD' },
    features: ['4WD Available','Adaptive Cruise','Blind Spot Monitor','360° Cameras','Ventilated Seats'],
    featuresAr: ['4WD متاح','كروز تكيفي','مراقبة جانبية','كاميرات 360°','مقاعد مهوية'],
  },
  {
    id: 'gac-gs8', brand: 'gac', name: 'GS8 2026', nameAr: 'GS8 2026',
    year: 2026, type: '7-Seat Luxury SUV', typeAr: 'إس يو في فاخر 7 مقاعد',
    range: null, battery: '2.0T Engine', power: '165 kW', accel: '7.8s',
    maxSpeed: 195, seats: 7, price: 'From $34,000', priceAr: 'من $34,000',
    image: '/images/vehicles/GAC_GS8_2026.png',
    specs: { length:'4930mm', width:'1920mm', height:'1780mm', wheelbase:'2920mm', weight:'1980 kg', drivetrain:'AWD' },
    features: ['7-Seat Configuration','ADAS Level 2','14.6" Touchscreen','Hands-free Tailgate','Luxury Interior'],
    featuresAr: ['7 مقاعد','ADAS L2','شاشة 14.6"','باب خلفي كهربائي','مقصورة فاخرة'],
  },
  // ── Geely ─────────────────────────────────────────────────────────────────
  {
    id: 'geely-geo-c', brand: 'geely', name: 'Geometry C 2023', nameAr: 'جيومتري C 2023',
    year: 2023, type: 'Electric SUV', typeAr: 'إس يو في كهربائي',
    range: 550, battery: '70 kWh', power: '150 kW', accel: '6.5s',
    maxSpeed: 150, seats: 5, price: 'From $25,000', priceAr: 'من $25,000',
    image: '/images/vehicles/Geely_Geometry_C_2023_side.png',
    specs: { length:'4432mm', width:'1833mm', height:'1608mm', wheelbase:'2700mm', weight:'1720 kg', drivetrain:'FWD' },
    features: ['CATL Battery Pack','Mobileye ADAS','Panoramic Sunroof','NFC Key Card','OTA Updates'],
    featuresAr: ['بطارية CATL','Mobileye ADAS','سقف بانورامي','بطاقة NFC','تحديثات هوائية'],
  },
  {
    id: 'geely-mk', brand: 'geely', name: 'MK Series', nameAr: 'سلسلة MK',
    year: 2023, type: 'Compact Sedan', typeAr: 'سيدان مدمج',
    range: null, battery: '1.5L Engine', power: '78 kW', accel: '11.0s',
    maxSpeed: 168, seats: 5, price: 'From $9,000', priceAr: 'من $9,000',
    image: '/images/vehicles/geelymk.png',
    specs: { length:'4547mm', width:'1705mm', height:'1480mm', wheelbase:'2700mm', weight:'1165 kg', drivetrain:'FWD' },
    features: ['Fuel-efficient Engine','5-Star Safety','Modern Dashboard','Bluetooth Audio','Spacious Cabin'],
    featuresAr: ['محرك اقتصادي','سلامة 5 نجوم','لوحة عصرية','صوت بلوتوث','مقصورة واسعة'],
  },
  {
    id: 'geely-radar', brand: 'geely', name: 'Radar ZB 2023', nameAr: 'رادار ZB 2023',
    year: 2023, type: 'Electric Pickup', typeAr: 'بيك أب كهربائي',
    range: 640, battery: '100 kWh', power: '200 kW', accel: '5.9s',
    maxSpeed: 180, seats: 5, price: 'From $40,000', priceAr: 'من $40,000',
    image: '/images/vehicles/GEELY_RADAR_ZB.png',
    specs: { length:'5385mm', width:'1975mm', height:'1810mm', wheelbase:'3200mm', weight:'2530 kg', drivetrain:'AWD' },
    features: ['Electric Pickup','Off-road Capability','Smart Towing','Fast Charging','360° Cameras'],
    featuresAr: ['بيك أب كهربائي','قدرة off-road','جر ذكي','شحن سريع','كاميرات 360°'],
  },
  // ── Haval ─────────────────────────────────────────────────────────────────
  {
    id: 'haval-h1', brand: 'haval', name: 'H1 2017', nameAr: 'H1 2017',
    year: 2017, type: 'Mini SUV', typeAr: 'ميني إس يو في',
    range: null, battery: '1.5L Engine', power: '75 kW', accel: '12.0s',
    maxSpeed: 160, seats: 5, price: 'From $12,000', priceAr: 'من $12,000',
    image: '/images/vehicles/HAVAL_H1_2017.png',
    specs: { length:'4000mm', width:'1735mm', height:'1625mm', wheelbase:'2520mm', weight:'1235 kg', drivetrain:'FWD' },
    features: ['Compact City SUV','Fuel Efficient','Manual & Auto','USB Charging','Alloy Wheels'],
    featuresAr: ['SUV مدمج','اقتصادي','يدوي وأوتوماتيك','شحن USB','جنوط سبيكة'],
  },
  {
    id: 'haval-h6', brand: 'haval', name: 'H6 2021', nameAr: 'H6 2021',
    year: 2021, type: 'Mid-size SUV', typeAr: 'إس يو في متوسط',
    range: null, battery: '1.5T / 2.0T', power: '150 kW', accel: '7.5s',
    maxSpeed: 185, seats: 5, price: 'From $20,000', priceAr: 'من $20,000',
    image: '/images/vehicles/HAVAL_H6_2021.png',
    specs: { length:'4653mm', width:'1886mm', height:'1730mm', wheelbase:'2738mm', weight:'1700 kg', drivetrain:'FWD/AWD' },
    features: ["China's Best-Selling SUV",'Digital Cockpit','L2 Autonomous','Panoramic Sunroof','Dual 12.3" Screens'],
    featuresAr: ['الأكثر مبيعاً في الصين','كوكبيت رقمي','استقلالية L2','سقف بانورامي','شاشتا 12.3"'],
  },
  {
    id: 'haval-h6-coupe', brand: 'haval', name: 'H6 Coupe 2016', nameAr: 'H6 كوبيه 2016',
    year: 2016, type: 'SUV Coupe', typeAr: 'كوبيه إس يو في',
    range: null, battery: '2.0T Engine', power: '150 kW', accel: '8.0s',
    maxSpeed: 180, seats: 5, price: 'From $17,000', priceAr: 'من $17,000',
    image: '/images/vehicles/HAVAL_H6_COUPE.png',
    specs: { length:'4560mm', width:'1895mm', height:'1667mm', wheelbase:'2681mm', weight:'1710 kg', drivetrain:'AWD' },
    features: ['Sporty Coupe Roofline','AWD System','Sport Mode','Leather Seats','8" Touchscreen'],
    featuresAr: ['خط سقف رياضي','نظام AWD','وضع رياضي','مقاعد جلدية','شاشة لمس 8"'],
  },
  {
    id: 'haval-jolion', brand: 'haval', name: 'Jolion 2020', nameAr: 'جوليون 2020',
    year: 2020, type: 'Compact SUV', typeAr: 'إس يو في مدمج',
    range: null, battery: '1.5T Engine', power: '110 kW', accel: '9.0s',
    maxSpeed: 185, seats: 5, price: 'From $17,000', priceAr: 'من $17,000',
    image: '/images/vehicles/HAVAL_JOLION_2020.png',
    specs: { length:'4472mm', width:'1841mm', height:'1653mm', wheelbase:'2700mm', weight:'1490 kg', drivetrain:'FWD' },
    features: ['Premium Interior','HAVAL Intelligence','10.25" Floating Screen','Active Safety Suite','Eye-catching Design'],
    featuresAr: ['مقصورة فاخرة','ذكاء HAVAL','شاشة عائمة 10.25"','حزمة سلامة','تصميم لافت'],
  },
  {
    id: 'haval-jolion-hev', brand: 'haval', name: 'Jolion HEV 2024', nameAr: 'جوليون HEV 2024',
    year: 2024, type: 'Hybrid SUV', typeAr: 'هجين إس يو في',
    range: null, battery: '1.5L + Hybrid', power: '120 kW', accel: '8.2s',
    maxSpeed: 185, seats: 5, price: 'From $22,000', priceAr: 'من $22,000',
    image: '/images/vehicles/HAVAL_JOLION_HEV_2024.png',
    specs: { length:'4472mm', width:'1841mm', height:'1653mm', wheelbase:'2700mm', weight:'1580 kg', drivetrain:'FWD' },
    features: ['Full Hybrid System','5.5L/100km Economy','Auto Start/Stop','Regenerative Braking','Smart Energy Mgmt'],
    featuresAr: ['هجين كامل','5.5 لتر/100كم','توقف تلقائي','فرملة تجديدية','طاقة ذكية'],
  },
  // ── MG ───────────────────────────────────────────────────────────────────
  {
    id: 'mg-5', brand: 'mg', name: 'MG 5', nameAr: 'إم جي 5',
    year: 2022, type: 'Electric Estate', typeAr: 'عائلي كهربائي',
    range: 400, battery: '61 kWh', power: '115 kW', accel: '7.7s',
    maxSpeed: 185, seats: 5, price: 'From $27,000', priceAr: 'من $27,000',
    image: '/images/vehicles/MG_5.png',
    specs: { length:'4600mm', width:'1818mm', height:'1506mm', wheelbase:'2680mm', weight:'1670 kg', drivetrain:'FWD' },
    features: ['Estate Body Style','DC Fast Charging','MGPILOT ADAS','Panoramic Roof','10.25" Multimedia'],
    featuresAr: ['هيكل عائلي','شحن DC','MGPILOT','سقف بانورامي','وسائط 10.25"'],
  },
  {
    id: 'mg-hs-phev', brand: 'mg', name: 'HS Plug-in Hybrid', nameAr: 'HS بلاق-إن هجين',
    year: 2020, type: 'Plug-in Hybrid SUV', typeAr: 'هجين قابل للشحن',
    range: 52, battery: '16.6 kWh', power: '165 kW', accel: '6.9s',
    maxSpeed: 200, seats: 5, price: 'From $30,000', priceAr: 'من $30,000',
    image: '/images/vehicles/MG_HS_PLUG_IN_HYBRID_2020.png',
    specs: { length:'4655mm', width:'1876mm', height:'1664mm', wheelbase:'2720mm', weight:'1895 kg', drivetrain:'FWD' },
    features: ['PHEV System','52km EV Range','45-min Fast Charge','Leather Seats','Premium Audio'],
    featuresAr: ['نظام PHEV','مدى EV 52 كم','شحن 45 دقيقة','مقاعد جلدية','صوت فاخر'],
  },
  {
    id: 'mg-one', brand: 'mg', name: 'MG One', nameAr: 'إم جي ون',
    year: 2022, type: 'Compact SUV', typeAr: 'إس يو في مدمج',
    range: null, battery: '1.5T Engine', power: '125 kW', accel: '8.5s',
    maxSpeed: 180, seats: 5, price: 'From $23,000', priceAr: 'من $23,000',
    image: '/images/vehicles/MG_ONE.png',
    specs: { length:'4579mm', width:'1868mm', height:'1635mm', wheelbase:'2710mm', weight:'1555 kg', drivetrain:'FWD' },
    features: ['Futuristic Exterior','Floating Display','All-around Cameras','Smart Driving Assist','Ventilated Seats'],
    featuresAr: ['مظهر مستقبلي','شاشة عائمة','كاميرات محيطية','مساعد قيادة','مقاعد مهوية'],
  },
  {
    id: 'mg-zs-ev', brand: 'mg', name: 'ZS EV 2022', nameAr: 'ZS EV 2022',
    year: 2022, type: 'Electric SUV', typeAr: 'إس يو في كهربائي',
    range: 440, battery: '51 kWh', power: '115 kW', accel: '8.2s',
    maxSpeed: 175, seats: 5, price: 'From $28,000', priceAr: 'من $28,000',
    image: '/images/vehicles/MG_ZS_EV_2022.png',
    specs: { length:'4314mm', width:'1809mm', height:'1620mm', wheelbase:'2585mm', weight:'1620 kg', drivetrain:'FWD' },
    features: ['Long-Range EV','DC Fast Charge','MGPILOT L2','360° View Camera','Connected Car Services'],
    featuresAr: ['EV مدى طويل','شحن DC','MGPILOT L2','كاميرا 360°','خدمات متصلة'],
  },
  // ── ORA ──────────────────────────────────────────────────────────────────
  {
    id: 'ora-good-cat', brand: 'ora', name: 'Good Cat', nameAr: 'قطة الخير',
    year: 2023, type: 'Electric Hatchback', typeAr: 'هاتشباك كهربائي',
    range: 500, battery: '63 kWh', power: '126 kW', accel: '8.5s',
    maxSpeed: 150, seats: 5, price: 'From $25,000', priceAr: 'من $25,000',
    image: '/images/vehicles/ORA_GOOD_CAT.png',
    specs: { length:'4235mm', width:'1825mm', height:'1596mm', wheelbase:'2650mm', weight:'1666 kg', drivetrain:'RWD' },
    features: ['Retro-Futurist Design','NVIDIA AI Chip','Face Recognition','Augmented HUD','One-pedal Driving'],
    featuresAr: ['تصميم ريترو','شريحة NVIDIA AI','تعرف وجه','HUD معزز','دواسة واحدة'],
  },
  // ── Volkswagen ────────────────────────────────────────────────────────────
  {
    id: 'vw-id4', brand: 'vw', name: 'ID.4 2026', nameAr: 'ID.4 2026',
    year: 2026, type: 'Electric SUV', typeAr: 'إس يو في كهربائي',
    range: 540, battery: '77 kWh', power: '210 kW', accel: '5.4s',
    maxSpeed: 180, seats: 5, price: 'From $38,000', priceAr: 'من $38,000',
    image: '/images/vehicles/VW_ID4_2026.png',
    specs: { length:'4584mm', width:'1852mm', height:'1640mm', wheelbase:'2766mm', weight:'2124 kg', drivetrain:'RWD/AWD' },
    features: ['AR Head-up Display','Travel Assist L2','ID.Light System','We Connect Plus','V2H Charging'],
    featuresAr: ['HUD واقع معزز','Travel Assist L2','ID.Light','We Connect Plus','شحن V2H'],
  },
  {
    id: 'vw-jetta', brand: 'vw', name: 'Jetta 2026', nameAr: 'جيتا 2026',
    year: 2026, type: 'Sedan', typeAr: 'سيدان',
    range: null, battery: '1.4T Engine', power: '110 kW', accel: '8.5s',
    maxSpeed: 200, seats: 5, price: 'From $22,000', priceAr: 'من $22,000',
    image: '/images/vehicles/VW_JETTA_2026.png',
    specs: { length:'4702mm', width:'1799mm', height:'1455mm', wheelbase:'2686mm', weight:'1310 kg', drivetrain:'FWD' },
    features: ['Virtual Cockpit Pro','ACC Stop & Go','LED Headlights','Discover Pro Navigation','German Engineering'],
    featuresAr: ['Virtual Cockpit Pro','تحكم سرعة','مصابيح LED','ملاحة Discover Pro','هندسة ألمانية'],
  },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

export function getBrandById(id: string): Brand | undefined {
  return BRANDS.find(b => b.id === id);
}

export function getVehiclesByBrand(brandId: string): Vehicle[] {
  return VEHICLES.filter(v => v.brand === brandId);
}

export function getVehicleById(id: string): Vehicle | undefined {
  return VEHICLES.find(v => v.id === id);
}

export function getAllVehicleIds(): string[] {
  return VEHICLES.map(v => v.id);
}

export function getAllBrandIds(): string[] {
  return BRANDS.map(b => b.id);
}
