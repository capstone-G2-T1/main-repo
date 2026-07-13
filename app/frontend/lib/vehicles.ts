export interface VehicleSpec {
  range: string;
  battery: string;
  power: string;
  acceleration: string;
  drivetrain: string;
  seating: number;
  length: string;
  width: string;
  height: string;
  wheelbase: string;
  topSpeed?: string;
  price?: string;
}

export interface Vehicle {
  id: string;
  name: string;
  nameAr: string;
  brand: string;
  brandLogo: string;
  year: number;
  image: string;
  spec: VehicleSpec;
  features: string[];
  featuresAr: string[];
}

export interface Brand {
  id: string;
  name: string;
  nameAr: string;
  logo: string;
  models: Vehicle[];
  description?: string;
  descriptionAr?: string;
  gradient?: string;
  primaryColor?: string;
  country?: string;
}

export const VEHICLES: Vehicle[] = [
  // BYD
  {
    id: "byd-dolphin-2025",
    name: "Dolphin 2025",
    nameAr: "دولفين 2025",
    brand: "BYD",
    brandLogo: "/brands/byd.svg",
    year: 2025,
    image: "/vehicles/byd-dolphin.jpg",
    spec: {
      range: "420 km",
      battery: "60.4 kWh",
      power: "201 hp",
      acceleration: "7.0 sec",
      drivetrain: "FWD",
      seating: 5,
      length: "4,290 mm",
      width: "1,770 mm",
      height: "1,570 mm",
      wheelbase: "2,700 mm",
      topSpeed: "160 km/h",
      price: "$32,000",
    },
    features: ["Blade Battery", "DiLink 4.0", "VTOL", "Panoramic Roof"],
    featuresAr: ["بطارية بليد", "DiLink 4.0", "VTOL", "سقف بانورامي"],
  },
  {
    id: "byd-seagull",
    name: "Seagull",
    nameAr: "سيغول",
    brand: "BYD",
    brandLogo: "/brands/byd.svg",
    year: 2024,
    image: "/vehicles/byd-seagull.jpg",
    spec: {
      range: "305 km",
      battery: "30.08 kWh",
      power: "75 hp",
      acceleration: "12.5 sec",
      drivetrain: "FWD",
      seating: 4,
      length: "3,780 mm",
      width: "1,715 mm",
      height: "1,540 mm",
      wheelbase: "2,500 mm",
      topSpeed: "130 km/h",
      price: "$14,000",
    },
    features: ["Compact Design", "Smart Connectivity", "Safety System"],
    featuresAr: ["تصميم مدمج", "اتصال ذكي", "نظام أمان"],
  },
  {
    id: "byd-seal-2025",
    name: "Seal 2025",
    nameAr: "سيل 2025",
    brand: "BYD",
    brandLogo: "/brands/byd.svg",
    year: 2025,
    image: "/vehicles/byd-seal.jpg",
    spec: {
      range: "570 km",
      battery: "82.5 kWh",
      power: "523 hp",
      acceleration: "3.8 sec",
      drivetrain: "AWD",
      seating: 5,
      length: "4,800 mm",
      width: "1,875 mm",
      height: "1,460 mm",
      wheelbase: "2,920 mm",
      topSpeed: "180 km/h",
      price: "$45,000",
    },
    features: ["Dual Motor", "Sporty Design", "Advanced Driver Assist"],
    featuresAr: ["محرك مزدوج", "تصميم رياضي", "مساعد السائق المتقدم"],
  },
  {
    id: "byd-sealion-7",
    name: "Sealion 7",
    nameAr: "سيليون 7",
    brand: "BYD",
    brandLogo: "/brands/byd.svg",
    year: 2024,
    image: "/vehicles/byd-sealion.jpg",
    spec: {
      range: "502 km",
      battery: "71.8 kWh",
      power: "215 hp",
      acceleration: "6.5 sec",
      drivetrain: "FWD",
      seating: 5,
      length: "4,530 mm",
      width: "1,860 mm",
      height: "1,670 mm",
      wheelbase: "2,720 mm",
      topSpeed: "170 km/h",
      price: "$38,000",
    },
    features: ["SUV Styling", "Large Cargo", "Panoramic Roof"],
    featuresAr: ["تصميم SUV", "مساحة شحن كبيرة", "سقف بانورامي"],
  },
  {
    id: "byd-song-plus-dmi",
    name: "Song Plus DM-i",
    nameAr: "سونغ بلس DM-i",
    brand: "BYD",
    brandLogo: "/brands/byd.svg",
    year: 2024,
    image: "/vehicles/byd-song.jpg",
    spec: {
      range: "110 km (EV)",
      battery: "18.3 kWh",
      power: "197 hp",
      acceleration: "8.5 sec",
      drivetrain: "FWD",
      seating: 5,
      length: "4,705 mm",
      width: "1,890 mm",
      height: "1,680 mm",
      wheelbase: "2,765 mm",
      topSpeed: "170 km/h",
      price: "$32,000",
    },
    features: ["Plug-in Hybrid", "V2L", "Smart Cabin"],
    featuresAr: ["هجين قابل للشحن", "V2L", "مقصورة ذكية"],
  },
  // Geely
  {
    id: "geely-geometry-c-2023",
    name: "Geometry C 2023",
    nameAr: "جيومتري سي 2023",
    brand: "Geely",
    brandLogo: "/brands/geely.svg",
    year: 2023,
    image: "/vehicles/geely-geometry-c.jpg",
    spec: {
      range: "450 km",
      battery: "70.0 kWh",
      power: "204 hp",
      acceleration: "6.9 sec",
      drivetrain: "FWD",
      seating: 5,
      length: "4,432 mm",
      width: "1,833 mm",
      height: "1,560 mm",
      wheelbase: "2,700 mm",
      topSpeed: "160 km/h",
      price: "$35,000",
    },
    features: ["Sporty Crossover", "Modern Design", "Smart Drive"],
    featuresAr: ["كروس أوفر رياضية", "تصميم عصري", "قيادة ذكية"],
  },
  {
    id: "geely-mk-series",
    name: "MK Series",
    nameAr: "إم كاي سيريز",
    brand: "Geely",
    brandLogo: "/brands/geely.svg",
    year: 2024,
    image: "/vehicles/geely-mk.jpg",
    spec: {
      range: "380 km",
      battery: "50.0 kWh",
      power: "163 hp",
      acceleration: "8.2 sec",
      drivetrain: "FWD",
      seating: 5,
      length: "4,370 mm",
      width: "1,780 mm",
      height: "1,580 mm",
      wheelbase: "2,650 mm",
      topSpeed: "150 km/h",
      price: "$28,000",
    },
    features: ["Urban SUV", "Efficient Drive", "Tech Features"],
    featuresAr: ["SUV حضرية", "قيادة فعالة", "مميزات تقنية"],
  },
  {
    id: "geely-radar-zb-2023",
    name: "Radar ZB 2023",
    nameAr: "رادار زد بي 2023",
    brand: "Geely",
    brandLogo: "/brands/geely.svg",
    year: 2023,
    image: "/vehicles/geely-radar.jpg",
    spec: {
      range: "520 km",
      battery: "80.0 kWh",
      power: "250 hp",
      acceleration: "5.8 sec",
      drivetrain: "AWD",
      seating: 5,
      length: "4,800 mm",
      width: "1,920 mm",
      height: "1,650 mm",
      wheelbase: "2,850 mm",
      topSpeed: "190 km/h",
      price: "$45,000",
    },
    features: ["Premium Crossover", "Long Range", "Luxury Feel"],
    featuresAr: ["كروس أوفر فاخرة", "مدى طويل", "إحساس فاخر"],
  },
  // VW
  {
    id: "vw-id4-2026",
    name: "ID.4 2026",
    nameAr: "آي دي 4 2026",
    brand: "VW",
    brandLogo: "/brands/vw.svg",
    year: 2026,
    image: "/vehicles/vw-id4.jpg",
    spec: {
      range: "520 km",
      battery: "82.0 kWh",
      power: "295 hp",
      acceleration: "6.0 sec",
      drivetrain: "AWD",
      seating: 5,
      length: "4,584 mm",
      width: "1,852 mm",
      height: "1,640 mm",
      wheelbase: "2,765 mm",
      topSpeed: "180 km/h",
      price: "$48,000",
    },
    features: ["Electric SUV", "Premium Brand", "Long Range"],
    featuresAr: ["SUV كهربائية", "علامة فاخرة", "مدى طويل"],
  },
  {
    id: "vw-jetta-2026",
    name: "Jetta 2026",
    nameAr: "جيتا 2026",
    brand: "VW",
    brandLogo: "/brands/vw.svg",
    year: 2026,
    image: "/vehicles/vw-jetta.jpg",
    spec: {
      range: "480 km",
      battery: "72.0 kWh",
      power: "201 hp",
      acceleration: "7.4 sec",
      drivetrain: "FWD",
      seating: 5,
      length: "4,702 mm",
      width: "1,790 mm",
      height: "1,459 mm",
      wheelbase: "2,686 mm",
      topSpeed: "170 km/h",
      price: "$38,000",
    },
    features: ["Sedan EV", "German Engineering", "Comfort"],
    featuresAr: ["سيدان كهربائية", "هندسة ألمانية", "راحة"],
  },
];

export const BRANDS: Brand[] = [
  {
    id: "byd",
    name: "BYD",
    nameAr: "بي واي دي",
    logo: "/brands/byd.svg",
    description: "Build Your Dreams — Leading Chinese automaker",
    descriptionAr: "بي واي دي — شركة صينية رائدة في تصنيع السيارات",
    gradient: "from-[#0a1628] to-[#1a2a4a]",
    primaryColor: "#1A3A6A",
    country: "China",
    models: VEHICLES.filter(v => v.brand === "BYD"),
  },
  {
    id: "geely",
    name: "Geely",
    nameAr: "جيلي",
    logo: "/brands/geely.svg",
    description: "Geely Holding — Chinese automotive excellence",
    descriptionAr: "مجموعة جيلي — التميز الصيني في صناعة السيارات",
    gradient: "from-[#0a0a1a] to-[#1a1a3a]",
    primaryColor: "#1A2A5A",
    country: "China",
    models: VEHICLES.filter(v => v.brand === "Geely"),
  },
  {
    id: "vw",
    name: "VW",
    nameAr: "فولكس فاجن",
    logo: "/brands/vw.svg",
    description: "Volkswagen — German precision, sold in China",
    descriptionAr: "فولكس فاجن — دقة ألمانية، تُباع في الصين",
    gradient: "from-[#0a0a2a] to-[#1a1a4a]",
    primaryColor: "#2A3A6A",
    country: "Germany",
    models: VEHICLES.filter(v => v.brand === "VW"),
  },
];

export function getVehicleById(id: string): Vehicle | undefined {
  return VEHICLES.find(v => v.id === id);
}

export function getVehiclesByBrand(brandId: string): Vehicle[] {
  const brand = BRANDS.find(b => b.id === brandId);
  return brand ? brand.models : [];
}

export function getAllVehicleNames(): string[] {
  return VEHICLES.map(v => v.name);
}

export function getBrandById(id: string): Brand | undefined {
  return BRANDS.find(b => b.id === id);
}

export interface VehicleMake {
  value: string;
  label: string;
  labelAr: string;
}

export const MAKES: VehicleMake[] = [
  { value: "BYD", label: "BYD", labelAr: "بي واي دي" },
  { value: "Geely", label: "Geely", labelAr: "جيلي" },
  { value: "VW", label: "VW", labelAr: "فولكس فاجن" },
];
