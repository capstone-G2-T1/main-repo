"""Deterministic Arabic/English entity extraction for vehicle questions."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rag.types import ExtractedEntities


@dataclass(frozen=True)
class VehicleAlias:
    make: str
    model: str
    aliases: tuple[str, ...]
    trims: tuple[str, ...] = ()


# Aliases are driven by the manuals currently shipped in data/raw_manuals.
VEHICLES: tuple[VehicleAlias, ...] = (
    VehicleAlias("BYD", "Dolphin", ("byd dolphin", "بي واي دي دولفين", "بي واي دي dolphin", "dolphin", "دولفين")),
    VehicleAlias("BYD", "Seal", ("byd seal", "بي واي دي سيل")),
    VehicleAlias("BYD", "Seagull", ("byd seagull", "بي واي دي سيجال")),
    VehicleAlias("BYD", "Sealion 7", ("byd sealion 7", "byd sealion7", "بي واي دي سيليون 7")),
    VehicleAlias("BYD", "Song Plus DM-i", ("byd song plus dm-i", "byd song plus", "بي واي دي سونج بلس")),
    VehicleAlias("GAC", "Empow", ("gac empow", "جي ايه سي امباو")),
    VehicleAlias("GAC", "GS3 Emzoom", ("gac gs3 emzoom", "gac gs3", "جي ايه سي gs3")),
    VehicleAlias("GAC", "GS4", ("gac gs4", "جي ايه سي gs4")),
    VehicleAlias("GAC", "GS8", ("gac gs8", "جي ايه سي gs8")),
    VehicleAlias("Geely", "Geometry C", ("geely geometry c", "جيلي جيومتري سي", "geometry c", "جيومتري سي")),
    VehicleAlias("Geely", "MK Series", ("geely mk series", "geely mk", "جيلي ام كي")),
    VehicleAlias("Geely", "Radar ZB", ("geely radar zb", "geely radar", "جيلي رادار")),
    VehicleAlias("Haval", "H1", ("haval h1", "هافال h1")),
    VehicleAlias("Haval", "H6", ("haval h6", "هافال h6")),
    VehicleAlias("Haval", "H6 Coupe", ("haval h6 coupe", "هافال h6 كوبيه")),
    VehicleAlias("Haval", "Jolion", ("haval jolion", "هافال جوليان", "jolion", "جوليان"), ("HEV",)),
    VehicleAlias("MG", "5", ("mg 5", "ام جي 5")),
    VehicleAlias("MG", "One", ("mg one", "ام جي ون")),
    VehicleAlias("MG", "ZS EV", ("mg zs ev", "ام جي زد اس", "ام جي زي اس")),
    VehicleAlias("MG", "HS Plug-in Hybrid", ("mg hs plug-in hybrid", "mg hs", "ام جي اتش اس")),
    VehicleAlias("ORA", "Good Cat", ("ora good cat", "اورا جود كات")),
    VehicleAlias("Volkswagen", "ID.4", ("volkswagen id.4", "volkswagen id4", "vw id.4", "فولكس فاجن id4")),
    VehicleAlias("Volkswagen", "Jetta", ("volkswagen jetta", "vw jetta", "فولكس فاجن جيتا")),
)

MAKE_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Volkswagen", ("volkswagen", "فولكس فاجن", "vw")),
    ("Geely", ("geely", "جيلي")),
    ("Haval", ("haval", "هافال")),
    ("BYD", ("byd", "بي واي دي")),
    ("GAC", ("gac", "جي ايه سي")),
    ("MG", ("mg", "ام جي")),
    ("ORA", ("ora", "اورا")),
)

SYSTEM_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("driver_assistance", ("مثبت السرعة", "مساعدة السائق", "adas", "cruise control")),
    ("climate_control", ("تكييف", "مكيف", "تبريد المقصورة", "air conditioning", "climate")),
    ("doors_locks", ("قفل", "اقفال", "باب", "ابواب", "door", "lock")),
    ("infotainment", ("شاشة", "بلوتوث", "نظام ترفيه", "infotainment", "bluetooth", "screen")),
    ("transmission", ("ناقل الحركة", "جير", "قير", "transmission", "gearbox")),
    ("steering", ("دركسيون", "توجيه", "مقود", "steering")),
    ("suspension", ("تعليق", "مساعدات", "suspension")),
    ("electrical", ("كهرباء", "كهربائي", "electrical")),
    ("lighting", ("انوار", "مصابيح", "اضاءة", "light", "headlamp")),
    ("charging", ("شحن", "شاحن", "charge", "charging")),
    ("battery", ("بطارية 12 فولت", "بطارية", "battery")),
    ("brakes", ("فرامل", "مكابح", "بريك", "brake", "abs", "epb")),
    ("tires", ("ضغط الاطارات", "ضغط إطارات", "اطارات", "إطارات", "كوشوك", "كفرات", "tire", "tyre", "tpms")),
    ("airbag", ("وسادة هوائية", "ايرباق", "ايرباغ", "airbag", "srs")),
    ("cooling", ("تبريد المحرك", "سائل التبريد", "coolant", "cooling")),
    ("engine", ("محرك", "موتور", "engine")),
    ("fuel", ("وقود", "بنزين", "fuel")),
)

KNOWN_WARNING_CODES = ("TPMS", "ABS", "EPB", "ESC", "SRS", "EV")
OBD_CODE = re.compile(r"\b[PBCU][0-9A-F]{4}\b", re.IGNORECASE)
YEAR = re.compile(r"\b(19[89]\d|20[0-4]\d)\b")


def _search_alias(text: str, aliases: tuple[str, ...]) -> bool:
    translation = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه"})
    collapsed = re.sub(r"[._\-/]+", " ", text.casefold().translate(translation))
    collapsed = " ".join(collapsed.split())
    return any(
        " ".join(re.sub(r"[._\-/]+", " ", alias.casefold().translate(translation)).split()) in collapsed
        for alias in aliases
    )


def extract_entities(question: str) -> ExtractedEntities:
    """Extract the first authoritative vehicle match and primary diagnostic entities."""
    if not question or not question.strip():
        return ExtractedEntities()

    text = question.casefold()
    make = model = trim = None

    # Prefer full make/model aliases over a make-only match.
    for vehicle in sorted(VEHICLES, key=lambda item: max(map(len, item.aliases)), reverse=True):
        if _search_alias(text, vehicle.aliases):
            make, model = vehicle.make, vehicle.model
            for candidate in vehicle.trims:
                if _search_alias(text, (candidate,)):
                    trim = candidate
                    break
            break

    if make is None:
        for canonical, aliases in MAKE_ALIASES:
            if _search_alias(text, aliases):
                make = canonical
                break

    year_match = YEAR.search(text)
    year = int(year_match.group(1)) if year_match else None

    vehicle_system = None
    for canonical, aliases in SYSTEM_ALIASES:
        if _search_alias(text, aliases):
            vehicle_system = canonical
            break

    obd_match = OBD_CODE.search(question.upper())
    error_code = obd_match.group(0).upper() if obd_match else None
    if error_code is None:
        uppercase = question.upper()
        for code in KNOWN_WARNING_CODES:
            if re.search(rf"(?<![A-Z0-9]){re.escape(code)}(?![A-Z0-9])", uppercase):
                error_code = code
                break

    return ExtractedEntities(make, model, trim, year, vehicle_system, error_code)
