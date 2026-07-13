// ─── Language ──────────────────────────────────────────────────────────────

export type Lang = 'en' | 'ar';

// ─── Translations ──────────────────────────────────────────────────────────

export const translations = {
  en: {
    nav: {
      home: 'Home', brands: 'Brands', models: 'Models',
      contact: 'Contact', login: 'Login', register: 'Sign Up',
    },
    hero: {
      eyebrow: 'The Electric Future is Now',
      title1: 'ALPHA', title2: 'EV',
      sub: "Explore the world's finest electric and hybrid vehicles — curated for performance, range, and elegance.",
      cta1: 'Explore Models', cta2: 'Our Brands',
      stat1: 'Brands', stat2: 'Models', stat3: 'Countries', stat4: 'Happy Owners',
    },
    showcase: {
      eyebrow: 'Fleet Overview', title: 'Explore All Models',
      sub: 'Filter by brand and navigate through our complete lineup.',
      all: 'All Brands', range: 'Range', battery: 'Battery', power: 'Power',
      seats: 'Seats', maxSpeed: 'Max Speed', accel: '0–100 km/h',
      prev: 'Previous', next: 'Next', details: 'Full Details',
      length: 'Length', width: 'Width', height: 'Height',
      wheelbase: 'Wheelbase', weight: 'Kerb Weight', drivetrain: 'Drivetrain',
    },
    vehicles: {
      eyebrow: 'Our Lineup', title: 'Every Model, One Place',
      sub: 'From city EVs to hybrid SUVs — your perfect drive is here.',
      details: 'View Details', viewAll: 'View All Models',
    },
    brands: {
      eyebrow: 'Our Partners', title: 'World-Class Brands',
      sub: 'We represent 7 iconic automotive brands from China, Germany, and beyond.',
      models: 'models', explore: 'Explore Brand',
    },
    vd: {
      back: '← Back to Models',
      specs: 'Specifications', features: 'Features',
      request: 'Request a Quote', brochure: 'Download Brochure',
    },
    auth: {
      loginTitle: 'Welcome Back',
      loginSub: 'Sign in to your Alpha EV account',
      email: 'Email Address', password: 'Password',
      remember: 'Remember me', login: 'Sign In',
      noAccount: "Don't have an account?",
      registerLink: 'Create Account',
      registerTitle: 'Create Account',
      registerSub: 'Join the Alpha EV community',
      name: 'Full Name', confirm: 'Confirm Password',
      haveAccount: 'Already have an account?',
      loginLink: 'Sign In',
      agree: 'By registering you agree to our Terms & Privacy Policy.',
      submit: 'Create Account',
    },
    chat: {
      title: 'Alpha EV Assistant', status: 'Online',
      placeholder: 'Ask about any vehicle...',
      welcome: "Hello! I'm your Alpha EV assistant. Ask me about any model, specs, pricing, or availability.",
      reply: 'Thanks for your message! Our team will get back to you shortly.',
    },
    footer: {
      desc: 'The premier destination for electric and hybrid vehicles in the region.',
      company: 'Company', about: 'About Alpha EV', careers: 'Careers', press: 'Press',
      brandsCol: 'Brands', allBrands: 'All Brands',
      support: 'Support', contact: 'Contact Us', faq: 'FAQ', warranty: 'Warranty',
      privacy: 'Privacy Policy', terms: 'Terms of Use',
      copy: '© 2025 Alpha EV. All rights reserved.',
    },
    cta: {
      title: 'Ready to Drive Electric?',
      sub: 'Visit our showroom or request a personalised quote from our team today.',
      btn1: 'Get a Quote', btn2: 'Find Showroom',
    },
    notFound: {
      title: 'Page Not Found',
      sub: "The page you're looking for doesn't exist.",
      back: 'Return Home',
    },
    loading: 'Loading...',
  },

  ar: {
    nav: {
      home: 'الرئيسية', brands: 'العلامات', models: 'الموديلات',
      contact: 'اتصل بنا', login: 'دخول', register: 'إنشاء حساب',
    },
    hero: {
      eyebrow: 'مستقبل الكهرباء حاضر الآن',
      title1: 'ألفا', title2: 'EV',
      sub: 'استكشف أرقى السيارات الكهربائية والهجينة في العالم — مختارة للأداء والمدى والأناقة.',
      cta1: 'استكشف الموديلات', cta2: 'علاماتنا التجارية',
      stat1: 'علامات تجارية', stat2: 'موديلات', stat3: 'دول', stat4: 'عملاء سعداء',
    },
    showcase: {
      eyebrow: 'نظرة على الأسطول', title: 'استكشف جميع الموديلات',
      sub: 'صفّ حسب العلامة وتنقل عبر التشكيلة الكاملة.',
      all: 'جميع العلامات', range: 'المدى', battery: 'البطارية', power: 'القوة',
      seats: 'المقاعد', maxSpeed: 'السرعة القصوى', accel: '0-100 كم/س',
      prev: 'السابق', next: 'التالي', details: 'التفاصيل الكاملة',
      length: 'الطول', width: 'العرض', height: 'الارتفاع',
      wheelbase: 'قاعدة العجلات', weight: 'وزن السيارة', drivetrain: 'نظام الدفع',
    },
    vehicles: {
      eyebrow: 'تشكيلتنا', title: 'كل الموديلات في مكان واحد',
      sub: 'من سيارات المدينة الكهربائية إلى SUV الهجينة — سيارتك المثالية هنا.',
      details: 'عرض التفاصيل', viewAll: 'عرض جميع الموديلات',
    },
    brands: {
      eyebrow: 'شركاؤنا', title: 'علامات عالمية بامتياز',
      sub: 'نمثل 7 علامات سيارات أيقونية من الصين وألمانيا وما بعدها.',
      models: 'موديل', explore: 'استكشف العلامة',
    },
    vd: {
      back: '→ العودة للموديلات',
      specs: 'المواصفات', features: 'المميزات',
      request: 'طلب عرض سعر', brochure: 'تحميل الكتالوج',
    },
    auth: {
      loginTitle: 'مرحباً بعودتك',
      loginSub: 'سجّل دخولك إلى حساب Alpha EV',
      email: 'البريد الإلكتروني', password: 'كلمة المرور',
      remember: 'تذكرني', login: 'تسجيل الدخول',
      noAccount: 'ليس لديك حساب؟',
      registerLink: 'إنشاء حساب',
      registerTitle: 'إنشاء حساب',
      registerSub: 'انضم إلى مجتمع Alpha EV',
      name: 'الاسم الكامل', confirm: 'تأكيد كلمة المرور',
      haveAccount: 'لديك حساب بالفعل؟',
      loginLink: 'تسجيل الدخول',
      agree: 'بالتسجيل أنت توافق على الشروط وسياسة الخصوصية.',
      submit: 'إنشاء الحساب',
    },
    chat: {
      title: 'مساعد Alpha EV', status: 'متصل',
      placeholder: 'اسأل عن أي سيارة...',
      welcome: 'مرحباً! أنا مساعد Alpha EV. اسألني عن أي موديل أو مواصفات أو أسعار.',
      reply: 'شكراً على رسالتك! سيتواصل معك فريقنا قريباً.',
    },
    footer: {
      desc: 'الوجهة الأولى للسيارات الكهربائية والهجينة في المنطقة.',
      company: 'الشركة', about: 'عن Alpha EV', careers: 'الوظائف', press: 'الصحافة',
      brandsCol: 'العلامات', allBrands: 'جميع العلامات',
      support: 'الدعم', contact: 'اتصل بنا', faq: 'الأسئلة الشائعة', warranty: 'الضمان',
      privacy: 'سياسة الخصوصية', terms: 'شروط الاستخدام',
      copy: '© 2025 Alpha EV. جميع الحقوق محفوظة.',
    },
    cta: {
      title: 'هل أنت مستعد لقيادة كهربائية؟',
      sub: 'زُر صالة العرض أو اطلب عرض سعر مخصص من فريقنا اليوم.',
      btn1: 'احصل على عرض سعر', btn2: 'ابحث عن معرض',
    },
    notFound: {
      title: 'الصفحة غير موجودة',
      sub: 'الصفحة التي تبحث عنها غير موجودة.',
      back: 'العودة للرئيسية',
    },
    loading: 'جاري التحميل...',
  },
} as const;

export type TranslationKey = keyof typeof translations.en;

export function t<
  S extends keyof typeof translations.en,
  K extends keyof typeof translations.en[S]
>(lang: Lang, section: S, key: K): string {
  return ((translations[lang]?.[section] as Record<string, string>)?.[key as string] ??
         (translations.en[section] as Record<string, string>)[key as string] ??
         String(key)) as string;
}

// ─── Class helpers ──────────────────────────────────────────────────────────

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

// ─── Format helpers ──────────────────────────────────────────────────────────

export function formatRange(km: number | null, lang: Lang): string {
  if (!km) return '—';
  return lang === 'ar' ? `${km} كم` : `${km} km`;
}

export function formatSpeed(kmh: number, lang: Lang): string {
  return lang === 'ar' ? `${kmh} كم/س` : `${kmh} km/h`;
}
