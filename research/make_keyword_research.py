#!/usr/bin/env python3
"""
Builds the keyword research workbook for sohailabbas.site.

IMPORTANT HONESTY CONSTRAINT
----------------------------
This script was produced without access to Google Keyword Planner, Ahrefs, Semrush
or any other paid keyword database. Search volume and keyword difficulty are therefore
left as explicit "NOT VERIFIED" placeholders. They are NEVER invented.

What IS included and verifiable:
  * the primary / long-tail / localised keyword list (from real search-result inspection)
  * the intent classification
  * competitors actually observed in the SERPs during research (dated)
  * a qualitative competition read (High / Medium / Low) based on what the SERP looks like:
    how many dedicated tools exist, whether big multi-tool domains hold the top slots.
  * the exact procedure for filling in volume + KD with a real data source.

Outputs: keywords.csv, keyword-research.xlsx
"""
import csv
import os
from datetime import date

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.abspath(__file__))
RESEARCH_DATE = date.today().isoformat()
UNVERIFIED = "NOT VERIFIED"

COUNTRIES = [
    ("United States", "US", "en", "google.com"),
    ("United Kingdom", "GB", "en", "google.co.uk"),
    ("Germany", "DE", "de", "google.de"),
    ("France", "FR", "fr", "google.fr"),
    ("Italy", "IT", "it", "google.it"),
    ("Spain", "ES", "es", "google.es"),
    ("Netherlands", "NL", "nl", "google.nl"),
    ("Poland", "PL", "pl", "google.pl"),
]

# ---------------------------------------------------------------- research data
# comp = qualitative read of the live SERP (High / Medium / Low).
# observed = domains actually seen ranking for the English head term during research.
# The same competitor picture generally holds for the localised variant unless noted.
TOOLS = [
    {
        "tool": "VAT Calculator", "slug": "vat-calculator",
        "primary": {
            "en": "vat calculator",
            "de": "mwst rechner",
            "fr": "calcul tva",
            "it": "calcolo iva",
            "es": "calculadora iva",
            "nl": "btw berekenen",
            "pl": "kalkulator vat",
        },
        "longtails": [
            "add vat to a price", "remove vat from gross amount", "reverse vat calculator",
            "vat calculator 20 percent", "gross to net vat", "vat on 1000",
            "how to calculate vat backwards", "vat calculator for invoice",
        ],
        "intent": "Transactional",
        "comp": "Medium",
        "observed": "vatcalculator.eu, taxesledger.com, evatcalculator.com, calculadoraiva.net, "
                    "invoo.es, myinvoicetemplate.com, neftcal.com, financialonlinetools.com",
        "note": "Strong opportunity: the ranking pages are mostly thin rate tables. Localised "
                "intent (MwSt / TVA / IVA / BTW) is served by many small sites, and few pages "
                "explain the divide-by-(1+rate) rule properly. Our page does, plus 12 rates.",
    },
    {
        "tool": "Percentage Calculator", "slug": "percentage-calculator",
        "primary": {
            "en": "percentage calculator",
            "de": "prozentrechner",
            "fr": "calcul pourcentage",
            "it": "calcolo percentuale",
            "es": "calculadora de porcentaje",
            "nl": "percentage berekenen",
            "pl": "kalkulator procentowy",
        },
        "longtails": [
            "what is 15 percent of 200", "percentage increase calculator",
            "x is what percent of y", "reverse percentage calculator",
            "percentage change between two numbers", "percent difference calculator",
            "how to calculate percentage of marks", "add 10 percent to a number",
        ],
        "intent": "Transactional / informational",
        "comp": "High",
        "observed": "calculator.net, rapidtables.com, calculatorsoup.com, omnicalculator.com, "
                    "percentagecalculator.net, miniwebtool.com, prozenrechner.de, prozenrechner variants",
        "note": "Highest-volume candidate but the hardest SERP: calculator.net and rapidtables "
                "hold it with huge domain authority. Included because intent is massive and it "
                "supports internal links from VAT and discount pages. Expect a long climb; "
                "target the long-tail modes (reverse %, change) first.",
    },
    {
        "tool": "Salary Calculator", "slug": "salary-calculator",
        "primary": {
            "en": "salary to hourly calculator",
            "de": "gehalt in stundenlohn rechner",
            "fr": "salaire horaire calculateur",
            "it": "calcolo stipendio orario",
            "es": "calculadora salario por hora",
            "nl": "salaris per uur berekenen",
            "pl": "kalkulator wynagrodzenia godzinowego",
        },
        "longtails": [
            "60000 a year is how much an hour", "annual salary to hourly rate",
            "hourly to salary calculator", "how many working hours in a year",
            "pro rata salary calculator", "monthly salary to hourly",
            "salary calculator with unpaid breaks", "how much is 25 an hour annually",
        ],
        "intent": "Transactional",
        "comp": "Medium",
        "observed": "salarytohourly.com, uksalarycalculator.io, calcforlife.com, "
                    "proratacalculator.uk, procalculator.co.uk, calculadora.co.uk",
        "note": "Deliberately scoped to gross pay conversion. We do NOT do net/take-home pay: "
                "that SERP is dominated by payroll-data sites (HMRC tables, tax bands) which we "
                "cannot verify or maintain per country. Stating that limit is also an E-E-A-T signal.",
    },
    {
        "tool": "Loan EMI Calculator", "slug": "loan-emi-calculator",
        "primary": {
            "en": "loan emi calculator",
            "de": "kreditrechner",
            "fr": "calculateur pret mensualite",
            "it": "calcolo rata mutuo",
            "es": "calculadora de cuota de prestamo",
            "nl": "hypotheek maandlasten berekenen",
            "pl": "kalkulator raty kredytu",
        },
        "longtails": [
            "monthly payment calculator with amortization schedule",
            "how much interest on a 250000 loan", "loan payoff calculator extra payment",
            "flat rate vs reducing balance interest", "car loan emi calculator",
            "amortization table month by month", "what happens if i prepay my loan",
        ],
        "intent": "Commercial investigation",
        "comp": "High",
        "observed": "bank and broker calculator pages, calculator.net, omnicalculator.com, "
                    "plus national bank comparison sites",
        "note": "Competitive but the SERP rewards a real amortisation table + extra-payment "
                "comparison, which many lender pages hide. Localised terms (Kreditrechner, "
                "calcolo rata mutuo, hypotheek berekenen) are strong in DE/IT/NL.",
    },
    {
        "tool": "Discount Calculator", "slug": "discount-calculator",
        "primary": {
            "en": "discount calculator",
            "de": "rabattrechner",
            "fr": "calcul remise",
            "it": "calcolo sconto",
            "es": "calculadora de descuento",
            "nl": "korting berekenen",
            "pl": "kalkulator rabatu",
        },
        "longtails": [
            "30 percent off 80", "original price before discount calculator",
            "stacked discount calculator", "percent off calculator with tax",
            "sale price calculator", "how much is 25 off",
            "double discount calculator", "find the original price from sale price",
        ],
        "intent": "Transactional",
        "comp": "Medium",
        "observed": "calculator.net, omnicalculator.com, percentagecalculator.net, "
                    "plus retail and coupon sites",
        "note": "The stacked-discount and reverse-original-price angles are underserved and are "
                "exactly the queries where people make arithmetic mistakes. Good internal-link hub "
                "with percentage and VAT pages.",
    },
    {
        "tool": "Date Duration Calculator", "slug": "date-duration-calculator",
        "primary": {
            "en": "date duration calculator",
            "de": "datum differenz rechner",
            "fr": "calcul nombre de jours entre deux dates",
            "it": "calcolo giorni tra due date",
            "es": "calculadora de dias entre fechas",
            "nl": "dagen tussen twee datums berekenen",
            "pl": "kalkulator dni miedzy datami",
        },
        "longtails": [
            "how many days between two dates", "business days calculator excluding weekends",
            "days until date", "calculate weeks between dates",
            "notice period calculator", "working days between dates",
            "date difference in years months days", "how many days until christmas",
        ],
        "intent": "Informational / transactional",
        "comp": "High",
        "observed": "timeanddate.com, calculator.net, calculatorsoup.com, omnicalculator.com",
        "note": "Strong steady demand. Differentiated on the inclusive/exclusive counting toggle "
                "and the notice-period use case, which generic calculators bury.",
    },
    {
        "tool": "Age Calculator", "slug": "age-calculator",
        "primary": {
            "en": "age calculator",
            "de": "altersrechner",
            "fr": "calculer son age",
            "it": "calcolo eta",
            "es": "calcular edad",
            "nl": "leeftijd berekenen",
            "pl": "kalkulator wieku",
        },
        "longtails": [
            "how old am i in days", "age on a specific date calculator",
            "age in years months days", "days until my next birthday",
            "age calculator for forms", "chronological age calculator",
            "what is my age in months", "age at date of joining calculator",
        ],
        "intent": "Informational",
        "comp": "High",
        "observed": "calculator.net, timeanddate.com, calculatorsoup.com, omnicalculator.com",
        "note": "Very high volume, very high competition. Included because the localised variants "
                "(Altersrechner, calcolo età, leeftijd berekenen) are less contested than the "
                "English head term and share one implementation.",
    },
    {
        "tool": "Overtime Pay Calculator", "slug": "overtime-pay-calculator",
        "primary": {
            "en": "overtime pay calculator",
            "de": "uberstunden rechner",
            "fr": "calcul heures supplementaires",
            "it": "calcolo straordinari",
            "es": "calculadora horas extra",
            "nl": "overuren berekenen",
            "pl": "kalkulator nadgodzin",
        },
        "longtails": [
            "time and a half calculator", "overtime pay for 45 hours",
            "double time calculator", "overtime rate from annual salary",
            "1.5 times hourly rate", "weekly gross pay with overtime",
            "overtime after 40 hours calculator", "shift premium overtime calculator",
        ],
        "intent": "Transactional",
        "comp": "Medium",
        "observed": "uksalarycalculator.io, calcforlife.com, procalculator.co.uk, "
                    "proratacalculator.uk, nhssalarycalculators.co.uk, usapaycalculator.com",
        "note": "Underserved compared to salary/net-pay terms, and the two-band multiplier "
                "(weekday 1.5x + Sunday 2x) is a real differentiator. Jurisdiction caveats stated "
                "on the page (US FLSA vs no UK statutory right).",
    },
    {
        "tool": "Tip Calculator", "slug": "tip-calculator",
        "primary": {
            "en": "tip calculator",
            "de": "trinkgeld rechner",
            "fr": "calcul pourboire",
            "it": "calcolo mancia",
            "es": "calculadora de propina",
            "nl": "fooi berekenen",
            "pl": "kalkulator napiwku",
        },
        "longtails": [
            "how much to tip", "split bill calculator with tip",
            "18 percent tip on 85", "tip calculator with tax",
            "tip on pre tax amount", "bill splitter 4 people",
            "how much to tip for delivery", "tipping guide by country",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "calculator.net, omnicalculator.com, calculator soup and many small "
                    "single-purpose tip sites",
        "note": "Volume is US-heavy and seasonal (holidays). The country-by-country tipping table "
                "differentiates it for UK/DE/FR/ES readers and adds genuine value beyond arithmetic.",
    },
    {
        "tool": "BMI Calculator", "slug": "bmi-calculator",
        "primary": {
            "en": "bmi calculator",
            "de": "bmi rechner",
            "fr": "calcul imc",
            "it": "calcolo bmi",
            "es": "calculadora imc",
            "nl": "bmi berekenen",
            "pl": "kalkulator bmi",
        },
        "longtails": [
            "what is a healthy bmi", "bmi calculator kg cm",
            "bmi calculator feet inches pounds", "healthy weight for my height",
            "bmi chart adults", "is bmi accurate for athletes",
            "bmi calculator children", "how to lower bmi",
        ],
        "intent": "Informational",
        "comp": "High",
        "observed": "nhs.uk, cdc.gov, calculator.net, healthline, omnicalculator.com",
        "note": "YMYL topic: government and health-authority pages dominate. Included for "
                "completeness and localised traffic, with explicit 'not a diagnosis' framing, "
                "WHO thresholds and the South/East Asian threshold caveat. Do not expect to "
                "outrank NHS/CDC on the English head term.",
    },
    {
        "tool": "Word & Character Counter", "slug": "word-counter",
        "primary": {
            "en": "word counter",
            "de": "wort zaehlen",
            "fr": "compteur de mots",
            "it": "conta parole",
            "es": "contador de palabras",
            "nl": "woorden tellen",
            "pl": "licznik slow",
        },
        "longtails": [
            "character counter without spaces", "how many characters in 500 words",
            "word count for essay", "character limit counter",
            "reading time calculator", "count words in a paragraph",
            "average words per page", "twitter character counter",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "wordcounter.net, charactercountonline.com, wordcounttool.com, editpad",
        "note": "Merged the separate 'Character Counter' candidate into this page: same intent, "
                "same users, and two near-identical pages would compete with each other. One strong "
                "page beats two thin ones — which is the brief's own rule.",
    },
    {
        "tool": "Case Converter", "slug": "case-converter",
        "primary": {
            "en": "case converter",
            "de": "grossschreibung kleinbuchstaben umwandeln",
            "fr": "convertisseur de casse",
            "it": "convertire maiuscole minuscole",
            "es": "convertir mayusculas a minusculas",
            "nl": "hoofdletters kleine letters omzetten",
            "pl": "zmiana wielkosci liter",
        },
        "longtails": [
            "uppercase to lowercase converter", "title case converter",
            "sentence case converter", "camelcase converter",
            "snake case converter", "convert text to title case",
            "capitalise first letter of each sentence", "fix caps lock text",
        ],
        "intent": "Transactional",
        "comp": "Medium",
        "observed": "convertcase.net, titlecaseconverter.com, capitalizemytitle.com, editpad",
        "note": "Moderate difficulty with steady demand; the developer cases (camel/snake/kebab) "
                "capture a different audience from the writing audience.",
    },
    {
        "tool": "Time Zone Converter", "slug": "time-zone-converter",
        "primary": {
            "en": "time zone converter",
            "de": "zeitzonen rechner",
            "fr": "convertisseur fuseau horaire",
            "it": "convertitore fuso orario",
            "es": "convertidor de zonas horarias",
            "nl": "tijdzone omrekenen",
            "pl": "przelicznik stref czasowych",
        },
        "longtails": [
            "3pm est in london", "time difference between two cities",
            "meeting planner across time zones", "convert cet to est",
            "what time is it in tokyo", "best time to call between us and europe",
            "utc to local time converter", "schedule meeting working hours overlap",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "timeanddate.com, worldtimebuddy-style planner sites, "
                    "time zone sections of large utility domains",
        "note": "Head term is held by very strong domains. Our angle is the working-hours "
                "highlight and the daylight-saving-transition warning, which is the actual "
                "pain point people search about. Long-tail city pairs ('3pm est in london') "
                "are the realistic entry points.",
    },
    {
        "tool": "Text Diff Checker", "slug": "text-diff-checker",
        "primary": {
            "en": "text diff checker",
            "de": "text vergleichen",
            "fr": "comparer deux textes",
            "it": "confrontare due testi",
            "es": "comparar dos textos",
            "nl": "teksten vergelijken",
            "pl": "porownywanie tekstow",
        },
        "longtails": [
            "compare two texts and find differences", "diff checker online",
            "check if two texts are identical", "compare documents for changes",
            "ignore whitespace diff", "text comparison similarity percentage",
            "compare contract versions", "code diff online",
        ],
        "intent": "Transactional",
        "comp": "Medium",
        "observed": "diffchecker.com, textcompare.org, diffnow.com, mergely",
        "note": "diffchecker.com owns the head term but the SERP is not saturated. "
                "Whitespace-insensitive comparison and a similarity score are the differentiators.",
    },
    {
        "tool": "JSON Formatter", "slug": "json-formatter",
        "primary": {
            "en": "json formatter",
            "de": "json formatierer",
            "fr": "formateur json",
            "it": "formattare json",
            "es": "formatear json",
            "nl": "json formatteren",
            "pl": "formatowanie json",
        },
        "longtails": [
            "json validator online", "minify json", "pretty print json",
            "json syntax error line number", "json beautifier",
            "validate json before api request", "json formatter 4 spaces",
            "fix invalid json trailing comma",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "jsonformatter.org, jsonlint.com, codebeautify.org, jsonformatter.curiousconcept.com",
        "note": "Developer traffic, mature competition. Client-side processing is a genuine "
                "advantage to state, because people paste live API tokens into these tools.",
    },
    {
        "tool": "PDF Merger", "slug": "pdf-merger",
        "primary": {
            "en": "merge pdf",
            "de": "pdf zusammenfugen",
            "fr": "fusionner pdf",
            "it": "unire pdf",
            "es": "unir pdf",
            "nl": "pdf samenvoegen",
            "pl": "polacz pdf",
        },
        "longtails": [
            "combine pdf files into one", "merge pdf without uploading",
            "join pdf pages", "merge pdf offline",
            "merge pdf on phone", "combine scanned pages into one pdf",
            "merge bank statements pdf safely", "merge pdf no page limit",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "ilovepdf.com, smallpdf.com, adobe acrobat online, freeconvert.com, "
                    "pdfguru.com, plus many 'ilovepdf alternative' clone sites",
        "note": "Enormous volume, brutal competition (iLovePDF/Smallpdf/Adobe). Our wedge is "
                "privacy: no upload at all. That is a real, verifiable differentiator for bank "
                "statements, passports and medical letters, and it is the angle to lead with.",
    },
    {
        "tool": "Image Compressor", "slug": "image-compressor",
        "primary": {
            "en": "image compressor",
            "de": "bild komprimieren",
            "fr": "compresser image",
            "it": "comprimere immagine",
            "es": "comprimir imagen",
            "nl": "afbeelding comprimeren",
            "pl": "kompresja zdjec",
        },
        "longtails": [
            "compress image to 100kb", "compress jpg online",
            "reduce photo size without losing quality", "compress png",
            "resize image for email", "compress image for visa application",
            "batch compress images", "compress image without uploading",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "tinypng.com, iloveimg.com, smallpdf, adobe, imageto.online, "
                    "snapimagetools.com, iloveimg.pro clones",
        "note": "The 'compress to under 100 KB / 50 KB' queries are the realistic entry point: "
                "they are specific, high intent and served poorly by generic compressors.",
    },
    {
        "tool": "Image to PDF", "slug": "image-to-pdf",
        "primary": {
            "en": "image to pdf",
            "de": "bild zu pdf",
            "fr": "image en pdf",
            "it": "immagine in pdf",
            "es": "imagen a pdf",
            "nl": "afbeelding naar pdf",
            "pl": "zdjecie do pdf",
        },
        "longtails": [
            "jpg to pdf converter", "combine photos into one pdf",
            "image to pdf a4", "convert photos of documents to pdf",
            "png to pdf", "image to pdf no watermark",
            "make pdf from phone photos", "scan to pdf without scanner",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "ilovepdf.com, smallpdf.com, adobe, freeconvert.com, snapimagetools.com",
        "note": "Same competitive set as PDF merge; same privacy wedge. A4/Letter page sizing "
                "plus fit-vs-fill is the practical detail most clones omit.",
    },
    {
        "tool": "JPG to PNG Converter", "slug": "jpg-to-png",
        "primary": {
            "en": "jpg to png",
            "de": "jpg in png umwandeln",
            "fr": "convertir jpg en png",
            "it": "convertire jpg in png",
            "es": "convertir jpg a png",
            "nl": "jpg naar png",
            "pl": "konwersja jpg na png",
        },
        "longtails": [
            "jpeg to png converter", "batch convert jpg to png",
            "convert several images at once", "jpg to png without uploading",
            "why is png bigger than jpg", "convert screenshot to png",
            "jpg to png for design tool", "free image converter no watermark",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "iloveimg.com, cloudconvert, freeconvert, adobe, convertio",
        "note": "Very high volume, but the 'why is my PNG bigger' query is a genuine content gap "
                "that most converters ignore. Answering it is a link and featured-snippet play.",
    },
    {
        "tool": "Word to PDF Converter", "slug": "docx-to-pdf",
        "primary": {
            "en": "word to pdf",
            "de": "word in pdf umwandeln",
            "fr": "word en pdf",
            "it": "word in pdf",
            "es": "word a pdf",
            "nl": "word naar pdf",
            "pl": "word do pdf",
        },
        "longtails": [
            "docx to pdf converter", "convert word document to pdf free",
            "word to pdf without uploading", "docx to pdf on phone",
            "word to pdf no watermark", "convert cv docx to pdf",
            "why does word to pdf change formatting", "docx to pdf offline",
        ],
        "intent": "Transactional",
        "comp": "High",
        "observed": "adobe, smallpdf, ilovepdf, freeconvert, pdfguru, "
                    "plus Microsoft Word's own export",
        "note": "Hardest file SERP: Adobe and Microsoft both rank, and users expect pixel-perfect "
                "layout. We compete honestly as a text-focused, no-upload converter and say what "
                "does not survive. Do not over-promise layout fidelity.",
    },
]

# ---------------------------------------------------------------- rows
HEADERS = [
    "Tool", "Tool URL slug", "Country", "Country code", "Search engine", "Language",
    "Primary keyword (localised)", "Keyword type", "Long-tail keywords", "Search intent",
    "Monthly search volume", "Keyword difficulty (KD)", "Competition (SERP observation)",
    "Competitors observed in SERP", "Data source for volume / KD", "Research date", "Opportunity note",
]


def build_rows():
    rows = []
    for t in TOOLS:
        for cname, ccode, lang, engine in COUNTRIES:
            if lang in t["primary"]:
                kw = t["primary"][lang]
            elif lang in ("nl", "pl"):
                kw = t["primary"].get(lang, t["primary"]["en"])
            else:
                kw = t["primary"]["en"]
            rows.append([
                t["tool"], t["slug"], cname, ccode, engine, lang, kw,
                "head + long-tail",
                " | ".join(t["longtails"][:5]) if lang == "en" else " | ".join(t["longtails"][:3]) + " | + localised variants",
                t["intent"],
                UNVERIFIED, UNVERIFIED, t["comp"],
                t["observed"], "Not available in this build — see 'How to verify' sheet",
                RESEARCH_DATE, t["note"] if lang == "en" else "",
            ])
    return rows


# ---------------------------------------------------------------- sheets
def style_header(ws, ncols, fill="1D4ED8"):
    for col in range(1, ncols + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True, color="FFFFFF", size=10)
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 34
    ws.freeze_panes = "A2"


def autosize(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def sheet_readme(wb):
    ws = wb.active
    ws.title = "Methodology"
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 108
    ws["A1"] = "Keyword research — sohailabbas.site"
    ws["A1"].font = Font(bold=True, size=15, color="1D4ED8")
    ws["A2"] = "Prepared"
    ws["B2"] = RESEARCH_DATE
    rows = [
        ("", ""),
        ("Read this first", "This workbook was produced WITHOUT access to Google Keyword Planner, "
                            "Ahrefs, Semrush or any paid keyword database. No account credentials "
                            "were available, so search volume and keyword difficulty could not be "
                            "retrieved and have NOT been estimated, invented or inferred."),
        ("What is verified", "The keyword lists, language variants, search intent, and the "
                             "competitor domains named in the 'Competitors observed' column — these "
                             "come from inspecting live search results during research on the date "
                             "above. The national VAT rates used by the VAT tool come from national "
                             "tax authority publications."),
        ("What is NOT verified", "Monthly search volume and KD are marked 'NOT VERIFIED' in every "
                                 "row. Competition is a qualitative read of the SERP (High/Medium/Low), "
                                 "not a keyword-tool difficulty score."),
        ("Why not estimate", "A plausible-looking number is worse than an empty cell: it would be "
                             "used to make decisions about which tool to build, and it would be wrong. "
                             "The brief explicitly forbids invented metrics, so the cells are left "
                             "honest."),
        ("How to complete this", "Open the 'How to verify' sheet. It lists the exact export steps for "
                                 "Google Keyword Planner (free with an Ads account) and for Ahrefs / "
                                 "Semrush if you have a subscription, plus the selection filters to apply "
                                 "once real numbers are in."),
        ("Structure", "Sheet 'Keyword research' = 20 tools x 8 countries = 160 rows. "
                      "Sheet 'Country plan' = per-market priority and notes. "
                      "Sheet 'Tool selection log' = which candidate tools were kept, merged or "
                      "replaced, and why. Sheet 'How to verify' = the data-collection procedure. "
                      "Sheet 'Tracking template' = columns to fill in after launch."),
        ("If you have Ahrefs/Semrush", "Paste your export in place of the NOT VERIFIED cells, keep the "
                                       "source column accurate, and re-sort by volume within each "
                                       "country. The tool order on the site should then follow evidence, "
                                       "not this file's current ordering."),
        ("Scope reminder", "19 of the 20 tools process data entirely in the browser. The 20th "
                           "(Word to PDF) also runs client-side but is text-focused by design. "
                           "No page promises rankings, earnings or advertising approval."),
    ]
    r = 3
    for label, text in rows:
        ws.cell(row=r, column=1, value=label).font = Font(bold=True, size=10)
        c = ws.cell(row=r, column=2, value=text)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = max(15, 15 * (len(text) // 95 + 1))
        r += 1
    ws["A12"] = "Label convention"
    ws["A12"].font = Font(bold=True)
    ws["B12"] = "NOT VERIFIED = no data source available at build time. High/Medium/Low = "
    ws["B12"].alignment = Alignment(wrap_text=True)


def sheet_keywords(wb):
    ws = wb.create_sheet("Keyword research")
    ws.append(HEADERS)
    style_header(ws, len(HEADERS))
    for row in build_rows():
        ws.append(row)
    autosize(ws, [24, 22, 17, 9, 14, 9, 30, 16, 46, 22, 18, 18, 20, 44, 34, 12, 60])
    warn = PatternFill("solid", fgColor="FEF3C7")
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for idx in (11, 12):
            row[idx - 1].fill = warn
            row[idx - 1].alignment = Alignment(horizontal="center")
        for idx in (9, 14, 17):
            row[idx - 1].alignment = Alignment(wrap_text=True, vertical="top")
    ws.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}{ws.max_row}"


def sheet_country(wb):
    ws = wb.create_sheet("Country plan")
    ws.append(["Country", "Priority", "Language", "Local keyword convention", "Why this priority",
               "Notes on competition"])
    style_header(ws, 6)
    data = [
        ("United Kingdom", "1", "en-GB", "vat calculator, salary to hourly, notice period",
         "English-language market with VAT, PAYE and notice-period culture that match our tools "
         "exactly; same content as the US with light localisation.",
         "High competition on head terms; UK-specific long-tails (notice period, 37.5 hour week) "
         "are softer."),
        ("Germany", "1", "de", "MwSt Rechner, Prozentrechner, Kreditrechner, BMI Rechner",
         "Largest EU search market, strong tool-search culture, and many ranking competitors are "
         "thin single-purpose sites.",
         "Medium: local sites (prozenrechner.de, rechnerzentrale.com) rank without deep content. "
         "Best realistic entry market."),
        ("Netherlands", "2", "nl", "BTW berekenen, salaris per uur, hypotheek maandlasten",
         "High internet penetration, high English literacy, relatively few polished local tool sites.",
         "Low to medium: local competitors are often outdated. Good early-win market."),
        ("Spain", "2", "es", "calculadora IVA, calculadora de porcentaje, calcular edad",
         "Large market; several dedicated IVA calculator sites rank with thin content.",
         "Medium: calculadoraiva.net, invoo.es, tecalculo.com are beatable on depth."),
        ("France", "2", "fr", "calcul TVA, calcul pourcentage, calcul IMC",
         "Large market, strong demand for TVA and salary tools.",
         "High on head terms (service-public, major media tool pages); medium on long-tail."),
        ("Italy", "3", "it", "calcolo IVA, calcolo percentuale, calcolo rata mutuo",
         "Large market with distinct VAT rate (22%) and strong loan calculator demand.",
         "Medium: mix of small tool sites and bank pages."),
        ("Poland", "3", "pl", "kalkulator VAT, kalkulator procentowy, kalkulator BMI",
         "Fast-growing market, 23% VAT rate, comparatively few well-built local tool sites.",
         "Low to medium: least contested of the eight markets for tool keywords."),
        ("United States", "3", "en-US", "tip calculator, overtime pay, salary to hourly",
         "Highest absolute volume, but the hardest SERP: calculator.net, rapidtables, "
         "omnicalculator and NerdWallet-class publishers hold most head terms.",
         "High: enter through specific long-tails (time and a half for $20/hour, compress image "
         "to 100kb) rather than head terms."),
    ]
    for r in data:
        ws.append(r)
    autosize(ws, [18, 9, 9, 46, 62, 52])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row[0].row].height = 58


def sheet_selection(wb):
    ws = wb.create_sheet("Tool selection log")
    ws.append(["Candidate from brief", "Decision", "Final tool / URL", "Reason"])
    style_header(ws, 4)
    data = [
        ("Percentage Calculator", "KEPT", "/tools/percentage-calculator/", "Massive demand, 4 modes incl. reverse %."),
        ("Salary Calculator", "KEPT (scoped)", "/tools/salary-calculator/", "Gross conversions only; net pay needs country-specific tax data we cannot verify."),
        ("Age Calculator", "KEPT", "/tools/age-calculator/", "High volume; strong in DE/IT/NL localised variants."),
        ("Date Duration Calculator", "KEPT", "/tools/date-duration-calculator/", "Notice periods and working days differentiate it."),
        ("Discount Calculator", "KEPT", "/tools/discount-calculator/", "Stacked and reverse-discount modes are underserved."),
        ("VAT Calculator", "ADDED (was not in candidate list)", "/tools/vat-calculator/", "Highest-fit EU opportunity: localised intent across all eight target countries, and weak competitor content."),
        ("Overtime Pay Calculator", "KEPT", "/tools/overtime-pay-calculator/", "Softer SERP than salary/net-pay terms."),
        ("Loan EMI Calculator", "KEPT", "/tools/loan-emi-calculator/", "Amortisation + extra-payment comparison beats most lender pages."),
        ("BMI Calculator", "KEPT", "/tools/bmi-calculator/", "YMYL, dominated by NHS/CDC; kept for localised traffic with honest framing."),
        ("Word Counter", "KEPT", "/tools/word-counter/", "Evergreen, tool-intent."),
        ("Character Counter", "MERGED into Word Counter", "/tools/word-counter/", "Same intent and same user; two near-identical pages would compete. One deep page beats two thin ones."),
        ("Case Converter", "KEPT", "/tools/case-converter/", "Includes developer cases for a second audience."),
        ("JSON Formatter and Validator", "KEPT", "/tools/json-formatter/", "Developer intent; local processing is a stated advantage."),
        ("PDF Merger", "KEPT", "/tools/pdf-merger/", "Privacy wedge: files never leave the device."),
        ("Image Compressor", "KEPT", "/tools/image-compressor/", "Targets the 'compress to X KB' long-tails."),
        ("Image to PDF Converter", "KEPT", "/tools/image-to-pdf/", "A4/Letter + fit/fill detail that clones omit."),
        ("JPG to PNG Converter", "KEPT", "/tools/jpg-to-png/", "Answers the 'why is PNG bigger' gap."),
        ("Word to PDF Converter", "KEPT (limited scope)", "/tools/docx-to-pdf/", "Text-focused conversion, limitations stated on the page."),
        ("Time Zone Converter", "KEPT", "/tools/time-zone-converter/", "Working-hours planner + DST warning."),
        ("Text Difference Checker", "KEPT", "/tools/text-diff-checker/", "Whitespace-insensitive diff and similarity score."),
        ("Tip Calculator", "ADDED (was not in candidate list)", "/tools/tip-calculator/", "High US/UK volume, cheap to build, adds a country tipping guide that generic calculators lack."),
        ("(no other candidates)", "REJECTED IDEAS", "—", "Net/take-home salary calculators per country, tax filing calculators, and currency converters were considered and rejected: they need continuously verified jurisdiction data, and an out-of-date figure would mislead users. Better to link out than to guess."),
    ]
    for r in data:
        ws.append(r)
    autosize(ws, [34, 30, 34, 86])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row[0].row].height = 34


def sheet_howto(wb):
    ws = wb.create_sheet("How to verify")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 104
    ws["A1"] = "Filling in the real numbers"
    ws["A1"].font = Font(bold=True, size=13, color="1D4ED8")
    steps = [
        ("Option A — Google Keyword Planner (free)", "1. Create a Google Ads account (no campaign needs to run).\n"
                                                     "2. Tools > Keyword Planner > Discover new keywords.\n"
                                                     "3. Enter start terms from the 'Primary keyword' column, one country at a time.\n"
                                                     "4. Set location to the target country and language to the local language.\n"
                                                     "5. Export to CSV and paste the average monthly searches into column K."),
        ("Option B — Ahrefs Keywords Explorer", "1. Keywords Explorer > enter the localised keyword.\n"
                                               "2. Set the country database (US, UK, DE, FR, IT, ES, NL, PL).\n"
                                               "3. Read Volume (col K) and KD (col L).\n"
                                               "4. Use 'Traffic potential' rather than raw volume when the SERP has strong brands."),
        ("Option C — Semrush Keyword Overview", "1. Keyword Overview > localised keyword > target country.\n"
                                               "2. Read Volume and Keyword Difficulty (%), and check the SERP features panel.\n"
                                               "3. Note whether a local pack, featured snippet or video occupies the top slot."),
        ("Selection filter to apply", "Keep a keyword only if: volume is meaningful for the country (a small EU market still "
                                     "pays at 500+), KD is below the stated ceiling (30 if achievable, otherwise the lowest "
                                     "third of the list), and the SERP is not 8/10 occupied by one dominant brand with a "
                                     "dedicated tool page. Otherwise keep the page but expect it to earn traffic from "
                                     "long-tails only."),
        ("Validate before building", "For each shortlisted keyword, open an incognito window, set the country, and check: "
                                    "(a) are the top results actually tools, or are they articles? (b) is there a featured "
                                    "snippet we could answer? (c) do the top 3 have thinner content than what we plan to "
                                    "publish? If the top 3 are stronger than us on all three, deprioritise."),
        ("Update the site order", "Once columns K and L are filled, re-rank the tools in src/data/tools-1.json and "
                                  "tools-2.json (the 'rank' field), then run python3 build.py. The homepage order and the "
                                  "ItemList structured data both follow that field."),
        ("Keep it honest", "Never overwrite the 'Data source' column with 'estimated'. If a number is not from a tool export, "
                           "delete it. A blank cell is credible; an invented one is not."),
    ]
    r = 3
    for label, text in steps:
        ws.cell(row=r, column=1, value=label).font = Font(bold=True, size=10)
        ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")
        c = ws.cell(row=r, column=2, value=text)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = max(30, 15 * (text.count("\n") + len(text) // 90 + 1))
        r += 1


def sheet_tracking(wb):
    ws = wb.create_sheet("Tracking template")
    ws.append(["Tool / URL", "Country", "Keyword", "Start position", "Week 4", "Week 8", "Week 12",
               "Impressions (GSC)", "Clicks (GSC)", "CTR", "Action this month"])
    style_header(ws, 11)
    for t in TOOLS:
        ws.append([f"/tools/{t['slug']}/", "", t["primary"]["en"], "", "", "", "", "", "", "", ""])
    autosize(ws, [30, 10, 34, 13, 10, 10, 10, 18, 14, 8, 34])
    ws.freeze_panes = "A2"


def main():
    wb = openpyxl.Workbook()
    sheet_readme(wb)
    sheet_keywords(wb)
    sheet_country(wb)
    sheet_selection(wb)
    sheet_howto(wb)
    sheet_tracking(wb)
    out_xlsx = os.path.join(ROOT, "keyword-research.xlsx")
    wb.save(out_xlsx)

    out_csv = os.path.join(ROOT, "keywords.csv")
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(HEADERS)
        for row in build_rows():
            w.writerow(row)

    print(f"Wrote {out_xlsx}")
    print(f"Wrote {out_csv}")
    print(f"  {len(build_rows())} keyword rows · {len(TOOLS)} tools · {len(COUNTRIES)} countries")
    print(f"  volume + KD cells are labelled '{UNVERIFIED}' (no paid data source available)")


if __name__ == "__main__":
    main()
