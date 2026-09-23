"""
Localized reply catalogue for Gyan's **admin console** tier.

Why this is one module instead of nine
──────────────────────────────────────
The learner catalogue keeps one file per language because its templates are
long prose. Admin answers are the opposite shape: a one-line lead-in wrapped
around a block of numbers. So the strings here are split into

  LEAD   — one sentence per answer, in all nine variants;
  LABEL  — the one- or two-word metric names used in the bullet lines.

A reviewer sees all nine renderings of a string side by side, and a builder
below composes `LEAD` + `LABEL` + the numbers from services/admin_chat_data.py.
Numbers, names, department names, competency names and course titles are never
translated — they are what the console, the CSV exports and iGOT itself show.

`services/chat_messages/__init__.py` is untouched by this module: its per-language
`T` tables must stay key-identical (tests/test_chat_messages.py), and the admin
tier is not part of the learner classifier's intent set.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

VARIANTS = ("en", "hi_latn", "hi", "mr", "bn", "gu", "or", "ta", "te")


def _t(table: Dict[str, Dict[str, str]], key: str, variant: str) -> str:
    row = table.get(key) or {}
    return row.get(variant) or row.get("en") or key


# ── One- or two-word metric names ─────────────────────────────────────────────

LABEL: Dict[str, Dict[str, str]] = {
    "officials": {"en": "Officials", "hi_latn": "Officials", "hi": "अधिकारी", "mr": "अधिकारी",
                  "bn": "আধিকারিক", "gu": "અધિકારીઓ", "or": "ଅଧିକାରୀ", "ta": "அலுவலர்கள்", "te": "అధికారులు"},
    "compliant": {"en": "Compliant", "hi_latn": "Compliant", "hi": "अनुपालन में", "mr": "अनुपालनात",
                  "bn": "অনুবর্তী", "gu": "અનુપાલનમાં", "or": "ଅନୁପାଳନରେ", "ta": "இணக்கம்", "te": "అనుసరణలో"},
    "inProgress": {"en": "In progress", "hi_latn": "In progress", "hi": "प्रगति में", "mr": "प्रगतीत",
                   "bn": "চলমান", "gu": "પ્રગતિમાં", "or": "ଚାଲୁଛି", "ta": "நடப்பில்", "te": "ప్రగతిలో"},
    "required": {"en": "Training required", "hi_latn": "Training required", "hi": "प्रशिक्षण आवश्यक",
                 "mr": "प्रशिक्षण आवश्यक", "bn": "প্রশিক্ষণ প্রয়োজন", "gu": "તાલીમ જરૂરી",
                 "or": "ତାଲିମ ଆବଶ୍ୟକ", "ta": "பயிற்சி தேவை", "te": "శిక్షణ అవసరం"},
    "compliance": {"en": "Training compliance", "hi_latn": "Training compliance", "hi": "प्रशिक्षण अनुपालन",
                   "mr": "प्रशिक्षण अनुपालन", "bn": "প্রশিক্ষণ অনুবর্তিতা", "gu": "તાલીમ અનુપાલન",
                   "or": "ତାଲିମ ଅନୁପାଳନ", "ta": "பயிற்சி இணக்கம்", "te": "శిక్షణ అనుసరణ"},
    "mandatory": {"en": "Mandatory (ACBP)", "hi_latn": "Mandatory (ACBP)", "hi": "अनिवार्य (ACBP)",
                  "mr": "अनिवार्य (ACBP)", "bn": "বাধ্যতামূলক (ACBP)", "gu": "ફરજિયાત (ACBP)",
                  "or": "ବାଧ୍ୟତାମୂଳକ (ACBP)", "ta": "கட்டாயம் (ACBP)", "te": "తప్పనిసరి (ACBP)"},
    "behind": {"en": "Behind", "hi_latn": "Behind", "hi": "पीछे", "mr": "मागे", "bn": "পিছিয়ে",
               "gu": "પાછળ", "or": "ପଛରେ", "ta": "பின்தங்கியோர்", "te": "వెనుకబడినవారు"},
    "avgMissing": {"en": "Avg missing skills", "hi_latn": "Avg missing skills", "hi": "औसत कमी वाले कौशल",
                   "mr": "सरासरी कमी कौशल्ये", "bn": "গড় ঘাটতি দক্ষতা", "gu": "સરેરાશ ખૂટતી કુશળતા",
                   "or": "ହାରାହାରି ଅଭାବ ଦକ୍ଷତା", "ta": "சராசரி குறை திறன்", "te": "సగటు లోపించిన నైపుణ్యాలు"},
    "department": {"en": "Department", "hi_latn": "Department", "hi": "विभाग", "mr": "विभाग",
                   "bn": "বিভাগ", "gu": "વિભાગ", "or": "ବିଭାଗ", "ta": "துறை", "te": "శాఖ"},
    "competency": {"en": "Competency", "hi_latn": "Competency", "hi": "दक्षता", "mr": "क्षमता",
                   "bn": "দক্ষতা", "gu": "ક્ષમતા", "or": "ଦକ୍ଷତା", "ta": "திறன்", "te": "సామర్థ్యం"},
    "shortage": {"en": "shortage index", "hi_latn": "shortage index", "hi": "कमी सूचकांक",
                 "mr": "कमतरता निर्देशांक", "bn": "ঘাটতি সূচক", "gu": "અછત સૂચકાંક",
                 "or": "ଅଭାବ ସୂଚକାଙ୍କ", "ta": "பற்றாக்குறை குறியீடு", "te": "కొరత సూచిక"},
    "status": {"en": "Status", "hi_latn": "Status", "hi": "स्थिति", "mr": "स्थिती", "bn": "অবস্থা",
               "gu": "સ્થિતિ", "or": "ସ୍ଥିତି", "ta": "நிலை", "te": "స్థితి"},
    "grade": {"en": "Grade", "hi_latn": "Grade", "hi": "श्रेणी", "mr": "श्रेणी", "bn": "শ্রেণি",
              "gu": "શ્રેણી", "or": "ଶ୍ରେଣୀ", "ta": "தரம்", "te": "గ్రేడ్"},
    "office": {"en": "Office", "hi_latn": "Office", "hi": "कार्यालय", "mr": "कार्यालय", "bn": "কার্যালয়",
               "gu": "કાર્યાલય", "or": "କାର୍ଯ୍ୟାଳୟ", "ta": "அலுவலகம்", "te": "కార్యాలయం"},
    "designation": {"en": "Designation", "hi_latn": "Designation", "hi": "पदनाम", "mr": "पदनाम",
                    "bn": "পদবি", "gu": "હોદ્દો", "or": "ପଦବୀ", "ta": "பதவி", "te": "హోదా"},
    "karma": {"en": "Karma points", "hi_latn": "Karma points", "hi": "कर्म अंक", "mr": "कर्म गुण",
              "bn": "কর্ম পয়েন্ট", "gu": "કર્મ પોઇન્ટ", "or": "କର୍ମ ପଏଣ୍ଟ", "ta": "கர்ம புள்ளிகள்",
              "te": "కర్మ పాయింట్లు"},
    "skillGaps": {"en": "Skill gaps", "hi_latn": "Skill gaps", "hi": "कौशल अंतर", "mr": "कौशल्य अंतर",
                  "bn": "দক্ষতার ঘাটতি", "gu": "કૌશલ્ય અંતર", "or": "କୌଶଳ ଅନ୍ତର", "ta": "திறன் இடைவெளி",
                  "te": "నైపుణ్య అంతరం"},
    "pending": {"en": "Pending", "hi_latn": "Pending", "hi": "लंबित", "mr": "प्रलंबित", "bn": "বকেয়া",
                "gu": "બાકી", "or": "ବାକି", "ta": "நிலுவையில்", "te": "పెండింగ్"},
    "completedCourses": {"en": "Courses completed", "hi_latn": "Courses completed", "hi": "पूर्ण किए गए कोर्स",
                         "mr": "पूर्ण झालेले कोर्स", "bn": "সম্পন্ন কোর্স", "gu": "પૂર્ણ થયેલા કોર્સ",
                         "or": "ସମ୍ପୂର୍ଣ୍ଣ କୋର୍ସ", "ta": "முடிக்கப்பட்ட படிப்புகள்", "te": "పూర్తయిన కోర్సులు"},
    "nudges": {"en": "Nudges sent", "hi_latn": "Nudges sent", "hi": "भेजे गए अनुस्मारक",
               "mr": "पाठवलेली स्मरणपत्रे", "bn": "পাঠানো অনুস্মারক", "gu": "મોકલેલા રીમાઇન્ડર",
               "or": "ପଠାଯାଇଥିବା ସ୍ମାରକ", "ta": "அனுப்பிய நினைவூட்டல்கள்", "te": "పంపిన రిమైండర్లు"},
    "plans": {"en": "Assigned plans", "hi_latn": "Assigned plans", "hi": "सौंपी गई योजनाएँ",
              "mr": "नेमलेल्या योजना", "bn": "বরাদ্দ পরিকল্পনা", "gu": "સોંપાયેલી યોજનાઓ",
              "or": "ଦିଆଯାଇଥିବା ଯୋଜନା", "ta": "ஒதுக்கப்பட்ட திட்டங்கள்", "te": "కేటాయించిన ప్రణాళికలు"},
    "trained12m": {"en": "Trained in last 12 months", "hi_latn": "Trained in last 12 months",
                   "hi": "पिछले 12 महीनों में प्रशिक्षित", "mr": "गेल्या १२ महिन्यांत प्रशिक्षित",
                   "bn": "গত ১২ মাসে প্রশিক্ষিত", "gu": "છેલ્લા ૧૨ મહિનામાં તાલીમબદ્ધ",
                   "or": "ଗତ ୧୨ ମାସରେ ତାଲିମପ୍ରାପ୍ତ", "ta": "கடந்த 12 மாதங்களில் பயிற்சி",
                   "te": "గత 12 నెలల్లో శిక్షణ"},
    "atTarget": {"en": "Competencies at target", "hi_latn": "Competencies at target",
                 "hi": "लक्ष्य पर दक्षताएँ", "mr": "लक्ष्यावरील क्षमता", "bn": "লক্ষ্যে থাকা দক্ষতা",
                 "gu": "લક્ષ્ય પરની ક્ષમતાઓ", "or": "ଲକ୍ଷ୍ୟରେ ଥିବା ଦକ୍ଷତା", "ta": "இலக்கிலுள்ள திறன்கள்",
                 "te": "లక్ష్యంలోని సామర్థ్యాలు"},
    "avgLevel": {"en": "Average FRAC level", "hi_latn": "Average FRAC level", "hi": "औसत FRAC स्तर",
                 "mr": "सरासरी FRAC स्तर", "bn": "গড় FRAC স্তর", "gu": "સરેરાશ FRAC સ્તર",
                 "or": "ହାରାହାରି FRAC ସ୍ତର", "ta": "சராசரி FRAC நிலை", "te": "సగటు FRAC స్థాయి"},
    "weekly": {"en": "Completions per week (last 4)", "hi_latn": "Completions per week (last 4)",
               "hi": "प्रति सप्ताह पूर्णता (अंतिम 4)", "mr": "दर आठवड्याला पूर्णता (शेवटचे ४)",
               "bn": "সাপ্তাহিক সম্পন্ন (শেষ ৪)", "gu": "સાપ્તાહિક પૂર્ણતા (છેલ્લા ૪)",
               "or": "ସାପ୍ତାହିକ ସମାପ୍ତି (ଶେଷ ୪)", "ta": "வாரத்திற்கு நிறைவுகள் (கடைசி 4)",
               "te": "వారానికి పూర్తయినవి (చివరి 4)"},
    "priority": {"en": "priority", "hi_latn": "priority", "hi": "प्राथमिकता", "mr": "प्राधान्य",
                 "bn": "অগ্রাধিকার", "gu": "પ્રાથમિકતા", "or": "ପ୍ରାଥମିକତା", "ta": "முன்னுரிமை",
                 "te": "ప్రాధాన్యత"},
    "action": {"en": "Action", "hi_latn": "Action", "hi": "कार्रवाई", "mr": "कृती", "bn": "পদক্ষেপ",
               "gu": "પગલું", "or": "କାର୍ଯ୍ୟ", "ta": "நடவடிக்கை", "te": "చర్య"},
    "level": {"en": "level", "hi_latn": "level", "hi": "स्तर", "mr": "स्तर", "bn": "স্তর", "gu": "સ્તર",
              "or": "ସ୍ତର", "ta": "நிலை", "te": "స్థాయి"},
    "target": {"en": "target", "hi_latn": "target", "hi": "लक्ष्य", "mr": "लक्ष्य", "bn": "লক্ষ্য",
               "gu": "લક્ષ્ય", "or": "ଲକ୍ଷ୍ୟ", "ta": "இலக்கு", "te": "లక్ష్యం"},
    "none": {"en": "none", "hi_latn": "koi nahi", "hi": "कोई नहीं", "mr": "काहीही नाही", "bn": "কিছু নেই",
             "gu": "કોઈ નહીં", "or": "କିଛି ନାହିଁ", "ta": "எதுவும் இல்லை", "te": "ఏమీ లేదు"},
    "nsoWide": {"en": "the whole NSO roster", "hi_latn": "poore NSO roster", "hi": "पूरे NSO रोस्टर",
                "mr": "संपूर्ण NSO रोस्टर", "bn": "সম্পূর্ণ NSO রোস্টার", "gu": "સમગ્ર NSO રોસ્ટર",
                "or": "ସମ୍ପୂର୍ଣ୍ଣ NSO ରୋଷ୍ଟର", "ta": "முழு NSO பட்டியல்", "te": "మొత్తం NSO రోస్టర్"},
    "scopeNote": {"en": "Scope", "hi_latn": "Scope", "hi": "दायरा", "mr": "व्याप्ती", "bn": "পরিসর",
                  "gu": "વ્યાપ", "or": "ପରିସର", "ta": "வரம்பு", "te": "పరిధి"},
    "suppressed": {"en": "fewer than 5 officials — percentages withheld",
                   "hi_latn": "5 se kam officials — percentage nahi dikhaya ja raha",
                   "hi": "5 से कम अधिकारी — प्रतिशत रोका गया", "mr": "५ पेक्षा कमी अधिकारी — टक्केवारी दिली नाही",
                   "bn": "৫ জনের কম — শতাংশ দেওয়া হয়নি", "gu": "૫ થી ઓછા અધિકારીઓ — ટકાવારી રોકી",
                   "or": "୫ରୁ କମ ଅଧିକାରୀ — ଶତକଡ଼ା ଦିଆଗଲା ନାହିଁ",
                   "ta": "5 க்கும் குறைவானோர் — சதவீதம் மறைக்கப்பட்டது",
                   "te": "5 కంటే తక్కువ — శాతం చూపలేదు"},
}


def label(key: str, variant: str) -> str:
    return _t(LABEL, key, variant)


# ── One lead-in sentence per answer ───────────────────────────────────────────

LEAD: Dict[str, Dict[str, str]] = {
    "overview": {
        "en": "Here is the current picture across {scope}:",
        "hi_latn": "{scope} ki abhi ki tasveer yeh hai:",
        "hi": "{scope} की वर्तमान स्थिति इस प्रकार है:",
        "mr": "{scope} ची सद्यस्थिती अशी आहे:",
        "bn": "{scope}-এর বর্তমান চিত্র এইরকম:",
        "gu": "{scope} ની હાલની સ્થિતિ આ પ્રમાણે છે:",
        "or": "{scope}ର ବର୍ତ୍ତମାନ ଚିତ୍ର ଏହିପରି:",
        "ta": "{scope} இன் தற்போதைய நிலை:",
        "te": "{scope} యొక్క ప్రస్తుత స్థితి:",
    },
    "officials": {
        "en": "Headcount across {scope}:",
        "hi_latn": "{scope} ka headcount:",
        "hi": "{scope} में अधिकारियों की संख्या:",
        "mr": "{scope} मधील अधिकाऱ्यांची संख्या:",
        "bn": "{scope}-এ আধিকারিকের সংখ্যা:",
        "gu": "{scope} માં અધિકારીઓની સંખ્યા:",
        "or": "{scope}ରେ ଅଧିକାରୀ ସଂଖ୍ୟା:",
        "ta": "{scope} இல் அலுவலர்களின் எண்ணிக்கை:",
        "te": "{scope} లో అధికారుల సంఖ్య:",
    },
    "compliance": {
        "en": "Training compliance across {scope}:",
        "hi_latn": "{scope} ka training compliance:",
        "hi": "{scope} का प्रशिक्षण अनुपालन:",
        "mr": "{scope} चे प्रशिक्षण अनुपालन:",
        "bn": "{scope}-এর প্রশিক্ষণ অনুবর্তিতা:",
        "gu": "{scope} નું તાલીમ અનુપાલન:",
        "or": "{scope}ର ତାଲିମ ଅନୁପାଳନ:",
        "ta": "{scope} இன் பயிற்சி இணக்கம்:",
        "te": "{scope} యొక్క శిక్షణ అనుసరణ:",
    },
    "mandatory": {
        "en": "Mandatory ACBP training across {scope}:",
        "hi_latn": "{scope} ki mandatory ACBP training:",
        "hi": "{scope} में अनिवार्य ACBP प्रशिक्षण:",
        "mr": "{scope} मधील अनिवार्य ACBP प्रशिक्षण:",
        "bn": "{scope}-এ বাধ্যতামূলক ACBP প্রশিক্ষণ:",
        "gu": "{scope} માં ફરજિયાત ACBP તાલીમ:",
        "or": "{scope}ରେ ବାଧ୍ୟତାମୂଳକ ACBP ତାଲିମ:",
        "ta": "{scope} இல் கட்டாய ACBP பயிற்சி:",
        "te": "{scope} లో తప్పనిసరి ACBP శిక్షణ:",
    },
    "departments": {
        "en": "The largest departments in {scope}, by training compliance:",
        "hi_latn": "{scope} ke sabse bade departments, compliance ke hisaab se:",
        "hi": "{scope} के सबसे बड़े विभाग, अनुपालन के अनुसार:",
        "mr": "{scope} मधील सर्वात मोठे विभाग, अनुपालनानुसार:",
        "bn": "{scope}-এর বৃহত্তম বিভাগগুলি, অনুবর্তিতা অনুযায়ী:",
        "gu": "{scope} ના સૌથી મોટા વિભાગો, અનુપાલન પ્રમાણે:",
        "or": "{scope}ର ସବୁଠାରୁ ବଡ଼ ବିଭାଗ, ଅନୁପାଳନ ଅନୁସାରେ:",
        "ta": "{scope} இன் மிகப்பெரிய துறைகள், இணக்கத்தின்படி:",
        "te": "{scope} లోని అతిపెద్ద శాఖలు, అనుసరణ ప్రకారం:",
    },
    "shortages": {
        "en": "The sharpest competency shortages in {scope}:",
        "hi_latn": "{scope} mein sabse badi competency shortages:",
        "hi": "{scope} में सबसे बड़ी दक्षता कमी:",
        "mr": "{scope} मधील सर्वात मोठ्या क्षमता कमतरता:",
        "bn": "{scope}-এ সবচেয়ে বড় দক্ষতার ঘাটতি:",
        "gu": "{scope} માં સૌથી મોટી ક્ષમતા અછત:",
        "or": "{scope}ରେ ସବୁଠାରୁ ବଡ଼ ଦକ୍ଷତା ଅଭାବ:",
        "ta": "{scope} இல் மிகப்பெரிய திறன் பற்றாக்குறைகள்:",
        "te": "{scope} లో అతిపెద్ద సామర్థ్య కొరతలు:",
    },
    "emerging": {
        "en": "What NSSTA should train next, on the {horizon}-month forecast for {scope}:",
        "hi_latn": "{scope} ke {horizon}-month forecast par NSSTA ko aage kya train karna chahiye:",
        "hi": "{scope} के {horizon}-माह पूर्वानुमान पर NSSTA को आगे क्या प्रशिक्षण देना चाहिए:",
        "mr": "{scope} च्या {horizon}-महिन्यांच्या अंदाजानुसार NSSTA ने पुढे काय प्रशिक्षण द्यावे:",
        "bn": "{scope}-এর {horizon}-মাসের পূর্বাভাসে NSSTA-র পরবর্তী প্রশিক্ষণ:",
        "gu": "{scope} ના {horizon}-માસના અંદાજ પર NSSTA એ આગળ શું તાલીમ આપવી:",
        "or": "{scope}ର {horizon}-ମାସ ପୂର୍ବାନୁମାନରେ NSSTA ପରବର୍ତ୍ତୀ ତାଲିମ:",
        "ta": "{scope} இன் {horizon}-மாத முன்னறிவிப்பில் NSSTA அடுத்து பயிற்றுவிக்க வேண்டியவை:",
        "te": "{scope} యొక్క {horizon}-నెలల అంచనాలో NSSTA తదుపరి శిక్షణ ఇవ్వవలసినవి:",
    },
    "trends": {
        "en": "How {scope} has moved between {first} and {last}:",
        "hi_latn": "{first} se {last} ke beech {scope} kaise badla:",
        "hi": "{first} से {last} के बीच {scope} में क्या बदला:",
        "mr": "{first} ते {last} दरम्यान {scope} मध्ये काय बदलले:",
        "bn": "{first} থেকে {last}-এর মধ্যে {scope} কীভাবে বদলেছে:",
        "gu": "{first} થી {last} વચ્ચે {scope} માં શું બદલાયું:",
        "or": "{first}ରୁ {last} ମଧ୍ୟରେ {scope}ରେ କଣ ବଦଳିଛି:",
        "ta": "{first} முதல் {last} வரை {scope} எப்படி மாறியது:",
        "te": "{first} నుండి {last} మధ్య {scope} ఎలా మారింది:",
    },
    "health": {
        "en": "Service health is **{overall}** as of {checked}:",
        "hi_latn": "{checked} tak service health **{overall}** hai:",
        "hi": "{checked} तक सेवा स्वास्थ्य **{overall}** है:",
        "mr": "{checked} पर्यंत सेवा स्थिती **{overall}** आहे:",
        "bn": "{checked} পর্যন্ত পরিষেবার অবস্থা **{overall}**:",
        "gu": "{checked} સુધી સેવા સ્થિતિ **{overall}** છે:",
        "or": "{checked} ସୁଦ୍ଧା ସେବା ସ୍ଥିତି **{overall}**:",
        "ta": "{checked} வரை சேவை நிலை **{overall}**:",
        "te": "{checked} వరకు సేవా స్థితి **{overall}**:",
    },
    "nudges": {
        "en": "{count} nudge(s) have been sent. The most recent:",
        "hi_latn": "{count} nudge bheje ja chuke hain. Sabse recent:",
        "hi": "{count} अनुस्मारक भेजे जा चुके हैं। सबसे हाल के:",
        "mr": "{count} स्मरणपत्रे पाठवली गेली आहेत. सर्वात अलीकडील:",
        "bn": "{count}টি অনুস্মারক পাঠানো হয়েছে। সাম্প্রতিকতম:",
        "gu": "{count} રીમાઇન્ડર મોકલાયા છે. સૌથી તાજેતરના:",
        "or": "{count} ସ୍ମାରକ ପଠାଯାଇଛି। ସବୁଠାରୁ ନୂଆ:",
        "ta": "{count} நினைவூட்டல்கள் அனுப்பப்பட்டுள்ளன. சமீபத்தியவை:",
        "te": "{count} రిమైండర్లు పంపబడ్డాయి. తాజావి:",
    },
    "assignments": {
        "en": "{count} training plan(s) assigned so far:",
        "hi_latn": "Ab tak {count} training plan assign hue hain:",
        "hi": "अब तक {count} प्रशिक्षण योजनाएँ सौंपी गई हैं:",
        "mr": "आतापर्यंत {count} प्रशिक्षण योजना नेमल्या आहेत:",
        "bn": "এখন পর্যন্ত {count}টি প্রশিক্ষণ পরিকল্পনা বরাদ্দ হয়েছে:",
        "gu": "અત્યાર સુધી {count} તાલીમ યોજનાઓ સોંપાઈ છે:",
        "or": "ଏପର୍ଯ୍ୟନ୍ତ {count} ତାଲିମ ଯୋଜନା ଦିଆଯାଇଛି:",
        "ta": "இதுவரை {count} பயிற்சித் திட்டங்கள் ஒதுக்கப்பட்டுள்ளன:",
        "te": "ఇప్పటివరకు {count} శిక్షణ ప్రణాళికలు కేటాయించబడ్డాయి:",
    },
    "needsTraining": {
        "en": "{count} official(s) in {scope} have not completed a single course yet:",
        "hi_latn": "{scope} mein {count} officials ne abhi tak ek bhi course complete nahi kiya:",
        "hi": "{scope} में {count} अधिकारियों ने अब तक एक भी कोर्स पूरा नहीं किया है:",
        "mr": "{scope} मध्ये {count} अधिकाऱ्यांनी अद्याप एकही कोर्स पूर्ण केलेला नाही:",
        "bn": "{scope}-এ {count} জন আধিকারিক এখনও একটিও কোর্স শেষ করেননি:",
        "gu": "{scope} માં {count} અધિકારીઓએ હજુ એક પણ કોર્સ પૂર્ણ કર્યો નથી:",
        "or": "{scope}ରେ {count} ଅଧିକାରୀ ଏପର୍ଯ୍ୟନ୍ତ ଗୋଟିଏ ବି କୋର୍ସ ସମ୍ପୂର୍ଣ୍ଣ କରିନାହାନ୍ତି:",
        "ta": "{scope} இல் {count} அலுவலர்கள் இன்னும் ஒரு படிப்பையும் முடிக்கவில்லை:",
        "te": "{scope} లో {count} అధికారులు ఇంకా ఒక్క కోర్సు కూడా పూర్తి చేయలేదు:",
    },
    "userFound": {
        "en": "**{name}** — {govId} · {userId}",
        "hi_latn": "**{name}** — {govId} · {userId}",
        "hi": "**{name}** — {govId} · {userId}",
        "mr": "**{name}** — {govId} · {userId}",
        "bn": "**{name}** — {govId} · {userId}",
        "gu": "**{name}** — {govId} · {userId}",
        "or": "**{name}** — {govId} · {userId}",
        "ta": "**{name}** — {govId} · {userId}",
        "te": "**{name}** — {govId} · {userId}",
    },
    "userNotFound": {
        "en": "I could not find an official matching **{term}** on the roster. Try the full name, the employee ID (EMP-1234), the iGOT user id (usr_…) or the official email.",
        "hi_latn": "Roster par **{term}** se koi official nahi mila. Poora naam, employee ID (EMP-1234), iGOT user id (usr_…) ya official email try karein.",
        "hi": "रोस्टर पर **{term}** से मेल खाता कोई अधिकारी नहीं मिला। पूरा नाम, कर्मचारी ID (EMP-1234), iGOT user id (usr_…) या आधिकारिक ईमेल आज़माएँ।",
        "mr": "रोस्टरवर **{term}** शी जुळणारा अधिकारी सापडला नाही. पूर्ण नाव, कर्मचारी ID (EMP-1234), iGOT user id (usr_…) किंवा अधिकृत ईमेल वापरून पहा.",
        "bn": "রোস্টারে **{term}**-এর সঙ্গে মেলে এমন কোনও আধিকারিক পাওয়া যায়নি। পুরো নাম, কর্মচারী ID (EMP-1234), iGOT user id (usr_…) বা সরকারি ইমেল দিন।",
        "gu": "રોસ્ટરમાં **{term}** સાથે મેળ ખાતો અધિકારી મળ્યો નથી. પૂરું નામ, કર્મચારી ID (EMP-1234), iGOT user id (usr_…) અથવા અધિકૃત ઈમેલ અજમાવો.",
        "or": "ରୋଷ୍ଟରରେ **{term}** ସହ ମେଳ ଖାଉଥିବା ଅଧିକାରୀ ମିଳିଲେ ନାହିଁ। ପୂରା ନାମ, କର୍ମଚାରୀ ID (EMP-1234), iGOT user id (usr_…) କିମ୍ବା ସରକାରୀ ଇମେଲ ଚେଷ୍ଟା କରନ୍ତୁ।",
        "ta": "**{term}** உடன் பொருந்தும் அலுவலர் பட்டியலில் இல்லை. முழுப் பெயர், ஊழியர் ID (EMP-1234), iGOT user id (usr_…) அல்லது அலுவலக மின்னஞ்சலை முயற்சிக்கவும்.",
        "te": "**{term}** కు సరిపోయే అధికారి రోస్టర్‌లో కనబడలేదు. పూర్తి పేరు, ఉద్యోగి ID (EMP-1234), iGOT user id (usr_…) లేదా అధికారిక ఇమెయిల్ ప్రయత్నించండి.",
    },
    "userAmbiguous": {
        "en": "**{term}** matches {count} officials. Which one?",
        "hi_latn": "**{term}** se {count} officials match hote hain. Kaunse?",
        "hi": "**{term}** से {count} अधिकारी मेल खाते हैं। कौन से?",
        "mr": "**{term}** शी {count} अधिकारी जुळतात. कोणते?",
        "bn": "**{term}**-এর সঙ্গে {count} জন মেলে। কোনজন?",
        "gu": "**{term}** સાથે {count} અધિકારીઓ મેળ ખાય છે. કયા?",
        "or": "**{term}** ସହ {count} ଅଧିକାରୀ ମେଳ ଖାଉଛନ୍ତି। କେଉଁ ଜଣ?",
        "ta": "**{term}** உடன் {count} அலுவலர்கள் பொருந்துகின்றனர். யார்?",
        "te": "**{term}** కు {count} అధికారులు సరిపోతున్నారు. ఎవరు?",
    },
    "userPrompt": {
        "en": "Tell me who to look up — a name, an employee ID (EMP-1234), an iGOT user id (usr_…) or an official email. For example: *\"tell me about Shikha Thakur\"*.",
        "hi_latn": "Bataiye kiske baare mein dekhna hai — naam, employee ID (EMP-1234), iGOT user id (usr_…) ya official email. Jaise: *\"Shikha Thakur ke baare mein batao\"*.",
        "hi": "बताइए किसके बारे में देखना है — नाम, कर्मचारी ID (EMP-1234), iGOT user id (usr_…) या आधिकारिक ईमेल। जैसे: *\"शिखा ठाकुर के बारे में बताइए\"*।",
        "mr": "कोणाबद्दल पाहायचे ते सांगा — नाव, कर्मचारी ID (EMP-1234), iGOT user id (usr_…) किंवा अधिकृत ईमेल.",
        "bn": "কার সম্পর্কে দেখতে চান বলুন — নাম, কর্মচারী ID (EMP-1234), iGOT user id (usr_…) বা সরকারি ইমেল।",
        "gu": "કોના વિશે જોવું છે તે કહો — નામ, કર્મચારી ID (EMP-1234), iGOT user id (usr_…) અથવા અધિકૃત ઈમેલ.",
        "or": "କାହା ବିଷୟରେ ଦେଖିବାକୁ ଚାହାନ୍ତି କୁହନ୍ତୁ — ନାମ, କର୍ମଚାରୀ ID (EMP-1234), iGOT user id (usr_…) କିମ୍ବା ସରକାରୀ ଇମେଲ।",
        "ta": "யாரைப் பற்றி பார்க்க வேண்டும் என்று சொல்லுங்கள் — பெயர், ஊழியர் ID (EMP-1234), iGOT user id (usr_…) அல்லது அலுவலக மின்னஞ்சல்.",
        "te": "ఎవరి గురించి చూడాలో చెప్పండి — పేరు, ఉద్యోగి ID (EMP-1234), iGOT user id (usr_…) లేదా అధికారిక ఇమెయిల్.",
    },
    "snapshotPending": {
        "en": "The workforce snapshot is still building ({status}), so competency levels are not available yet. Training and compliance numbers are — ask me again in a minute for the rest.",
        "hi_latn": "Workforce snapshot abhi ban raha hai ({status}), isliye competency levels abhi available nahi hain. Training aur compliance numbers available hain — baaki ke liye ek minute baad poochhiye.",
        "hi": "कार्यबल स्नैपशॉट अभी बन रहा है ({status}), इसलिए दक्षता स्तर अभी उपलब्ध नहीं हैं। प्रशिक्षण और अनुपालन के आंकड़े उपलब्ध हैं — बाकी के लिए एक मिनट बाद पूछिए।",
        "mr": "कार्यबल स्नॅपशॉट अजून तयार होत आहे ({status}), त्यामुळे क्षमता स्तर उपलब्ध नाहीत. प्रशिक्षण आकडे उपलब्ध आहेत.",
        "bn": "কর্মীবাহিনীর স্ন্যাপশট এখনও তৈরি হচ্ছে ({status}), তাই দক্ষতার স্তর এখনও নেই। প্রশিক্ষণের সংখ্যা রয়েছে।",
        "gu": "વર્કફોર્સ સ્નેપશોટ હજુ બની રહ્યો છે ({status}), તેથી ક્ષમતા સ્તર ઉપલબ્ધ નથી. તાલીમના આંકડા ઉપલબ્ધ છે.",
        "or": "କର୍ମଶକ୍ତି ସ୍ନାପସଟ ଏବେ ତିଆରି ହେଉଛି ({status}), ତେଣୁ ଦକ୍ଷତା ସ୍ତର ଉପଲବ୍ଧ ନାହିଁ। ତାଲିମ ସଂଖ୍ୟା ଉପଲବ୍ଧ।",
        "ta": "பணியாளர் ஸ்னாப்ஷாட் இன்னும் உருவாகிறது ({status}), எனவே திறன் நிலைகள் இப்போது இல்லை. பயிற்சி எண்கள் உள்ளன.",
        "te": "వర్క్‌ఫోర్స్ స్నాప్‌షాట్ ఇంకా తయారవుతోంది ({status}), కాబట్టి సామర్థ్య స్థాయిలు ఇంకా లేవు. శిక్షణ సంఖ్యలు అందుబాటులో ఉన్నాయి.",
    },
    "nav": {
        "en": "Opening **{label}** for you.",
        "hi_latn": "Aapke liye **{label}** khol raha hoon.",
        "hi": "आपके लिए **{label}** खोल रहा हूँ।",
        "mr": "तुमच्यासाठी **{label}** उघडत आहे.",
        "bn": "আপনার জন্য **{label}** খুলছি।",
        "gu": "તમારા માટે **{label}** ખોલી રહ્યો છું.",
        "or": "ଆପଣଙ୍କ ପାଇଁ **{label}** ଖୋଲୁଛି।",
        "ta": "உங்களுக்காக **{label}** திறக்கிறேன்.",
        "te": "మీ కోసం **{label}** తెరుస్తున్నాను.",
    },
    "error": {
        "en": "I could not read that from the console just now ({detail}). The dashboard panels still have the numbers.",
        "hi_latn": "Abhi console se yeh nahi padh saka ({detail}). Dashboard panels mein numbers maujood hain.",
        "hi": "अभी कंसोल से यह नहीं पढ़ पाया ({detail})। डैशबोर्ड पैनल में आंकड़े मौजूद हैं।",
        "mr": "सध्या कन्सोलमधून हे वाचता आले नाही ({detail}). डॅशबोर्ड पॅनेलमध्ये आकडे आहेत.",
        "bn": "এই মুহূর্তে কনসোল থেকে এটি পড়া যায়নি ({detail})। ড্যাশবোর্ড প্যানেলে সংখ্যা রয়েছে।",
        "gu": "અત્યારે કન્સોલમાંથી આ વાંચી શક્યો નહીં ({detail}). ડેશબોર્ડ પેનલમાં આંકડા છે.",
        "or": "ଏବେ କନସୋଲରୁ ଏହା ପଢ଼ିପାରିଲି ନାହିଁ ({detail})। ଡ୍ୟାସବୋର୍ଡ ପ୍ୟାନେଲରେ ସଂଖ୍ୟା ଅଛି।",
        "ta": "இப்போது கன்சோலில் இருந்து இதைப் படிக்க முடியவில்லை ({detail}). டாஷ்போர்டு பலகைகளில் எண்கள் உள்ளன.",
        "te": "ప్రస్తుతం కన్సోల్ నుండి దీన్ని చదవలేకపోయాను ({detail}). డాష్‌బోర్డ్ ప్యానెల్‌లలో సంఖ్యలు ఉన్నాయి.",
    },
    "capabilities": {
        "en": ("I'm **Gyan**, and on this console I answer from the live admin data.\n"
               "\n"
               "• **Workforce** — headcount, training compliance, ACBP progress, who is behind\n"
               "• **Analysis** — competency shortages, department breakdown, trends, emerging skills\n"
               "• **One official** — *\"tell me about Shikha Thakur\"* or a user id, employee ID or email\n"
               "• **Operations** — nudges sent, training plans assigned, service health\n"
               "• **Navigation** — I can open any admin tab, the learner dashboard or the public site\n"
               "• **Anything Gyan already knew** — MoSPI, FRAC, GDP/CPI, the platform, theme and language\n"
               "\n"
               "Name a department, office or service tier in your question and I will scope the answer to it."),
        "hi_latn": ("Main **Gyan** hoon, aur is console par live admin data se jawab deta hoon.\n"
                    "\n"
                    "• **Workforce** — headcount, compliance, ACBP progress, kaun peeche hai\n"
                    "• **Analysis** — competency shortages, department breakdown, trends, emerging skills\n"
                    "• **Ek official** — *\"Shikha Thakur ke baare mein batao\"*, ya user id / EMP ID / email\n"
                    "• **Operations** — nudges, assigned training plans, service health\n"
                    "• **Navigation** — koi bhi admin tab, learner dashboard ya public site khol sakta hoon\n"
                    "• **Gyan ka purana sab kuch** — MoSPI, FRAC, GDP/CPI, platform, theme aur language\n"
                    "\n"
                    "Sawaal mein department, office ya tier bataiye to jawab usi scope ka hoga."),
        "hi": ("मैं **ज्ञान** हूँ, और इस कंसोल पर live admin डेटा से उत्तर देता हूँ।\n"
               "\n"
               "• **कार्यबल** — संख्या, प्रशिक्षण अनुपालन, ACBP प्रगति, कौन पीछे है\n"
               "• **विश्लेषण** — दक्षता कमी, विभागवार ब्योरा, रुझान, उभरते कौशल\n"
               "• **किसी एक अधिकारी** — *\"शिखा ठाकुर के बारे में बताइए\"*, या user id / EMP ID / ईमेल\n"
               "• **संचालन** — भेजे गए अनुस्मारक, सौंपी गई योजनाएँ, सेवा स्वास्थ्य\n"
               "• **नेविगेशन** — कोई भी admin tab, learner dashboard या सार्वजनिक साइट खोल सकता हूँ\n"
               "• **ज्ञान की पुरानी सभी क्षमताएँ** — MoSPI, FRAC, GDP/CPI, platform, theme और भाषा\n"
               "\n"
               "प्रश्न में विभाग, कार्यालय या श्रेणी बताइए तो उत्तर उसी दायरे का होगा।"),
        "mr": ("मी **ज्ञान** आहे आणि या कन्सोलवर live admin डेटावरून उत्तर देतो.\n"
               "\n"
               "• **कार्यबल** — संख्या, अनुपालन, ACBP प्रगती, कोण मागे आहे\n"
               "• **विश्लेषण** — क्षमता कमतरता, विभागनिहाय तपशील, कल, उदयोन्मुख कौशल्ये\n"
               "• **एका अधिकाऱ्याबद्दल** — नाव, user id, EMP ID किंवा ईमेल द्या\n"
               "• **संचालन** — स्मरणपत्रे, नेमलेल्या योजना, सेवा स्थिती\n"
               "• **नेव्हिगेशन** — कोणताही admin tab किंवा learner dashboard उघडू शकतो"),
        "bn": ("আমি **জ্ঞান**, এই কনসোলে live admin ডেটা থেকে উত্তর দিই।\n"
               "\n"
               "• **কর্মীবাহিনী** — সংখ্যা, অনুবর্তিতা, ACBP অগ্রগতি, কারা পিছিয়ে\n"
               "• **বিশ্লেষণ** — দক্ষতার ঘাটতি, বিভাগভিত্তিক হিসাব, প্রবণতা, উদীয়মান দক্ষতা\n"
               "• **একজন আধিকারিক** — নাম, user id, EMP ID বা ইমেল দিন\n"
               "• **পরিচালনা** — অনুস্মারক, বরাদ্দ পরিকল্পনা, পরিষেবার অবস্থা\n"
               "• **নেভিগেশন** — যেকোনো admin tab বা learner dashboard খুলতে পারি"),
        "gu": ("હું **જ્ઞાન** છું, આ કન્સોલ પર live admin ડેટામાંથી જવાબ આપું છું.\n"
               "\n"
               "• **કાર્યબળ** — સંખ્યા, અનુપાલન, ACBP પ્રગતિ, કોણ પાછળ છે\n"
               "• **વિશ્લેષણ** — ક્ષમતા અછત, વિભાગવાર વિગત, વલણ, ઉભરતા કૌશલ્યો\n"
               "• **એક અધિકારી** — નામ, user id, EMP ID અથવા ઈમેલ આપો\n"
               "• **સંચાલન** — રીમાઇન્ડર, સોંપાયેલી યોજનાઓ, સેવા સ્થિતિ\n"
               "• **નેવિગેશન** — કોઈપણ admin tab અથવા learner dashboard ખોલી શકું છું"),
        "or": ("ମୁଁ **ଜ୍ଞାନ**, ଏହି କନସୋଲରେ live admin ଡାଟାରୁ ଉତ୍ତର ଦିଏ।\n"
               "\n"
               "• **କର୍ମଶକ୍ତି** — ସଂଖ୍ୟା, ଅନୁପାଳନ, ACBP ପ୍ରଗତି, କିଏ ପଛରେ\n"
               "• **ବିଶ୍ଳେଷଣ** — ଦକ୍ଷତା ଅଭାବ, ବିଭାଗୱାରୀ ବିବରଣୀ, ଧାରା, ଉଦୀୟମାନ ଦକ୍ଷତା\n"
               "• **ଜଣେ ଅଧିକାରୀ** — ନାମ, user id, EMP ID କିମ୍ବା ଇମେଲ ଦିଅନ୍ତୁ\n"
               "• **ପରିଚାଳନା** — ସ୍ମାରକ, ଦିଆଯାଇଥିବା ଯୋଜନା, ସେବା ସ୍ଥିତି\n"
               "• **ନେଭିଗେସନ** — ଯେକୌଣସି admin tab କିମ୍ବା learner dashboard ଖୋଲିପାରିବି"),
        "ta": ("நான் **ஞான்**, இந்தக் கன்சோலில் நேரடி admin தரவிலிருந்து பதிலளிக்கிறேன்.\n"
               "\n"
               "• **பணியாளர்** — எண்ணிக்கை, இணக்கம், ACBP முன்னேற்றம், யார் பின்தங்கியுள்ளனர்\n"
               "• **பகுப்பாய்வு** — திறன் பற்றாக்குறை, துறை வாரியான விவரம், போக்கு, வளர் திறன்கள்\n"
               "• **ஒரு அலுவலர்** — பெயர், user id, EMP ID அல்லது மின்னஞ்சல் தரவும்\n"
               "• **செயல்பாடுகள்** — நினைவூட்டல்கள், ஒதுக்கிய திட்டங்கள், சேவை நிலை\n"
               "• **வழிசெலுத்தல்** — எந்த admin tab அல்லது learner dashboard-ஐயும் திறக்க முடியும்"),
        "te": ("నేను **జ్ఞాన్**, ఈ కన్సోల్‌లో live admin డేటా నుండి సమాధానం ఇస్తాను.\n"
               "\n"
               "• **సిబ్బంది** — సంఖ్య, అనుసరణ, ACBP ప్రగతి, ఎవరు వెనుకబడ్డారు\n"
               "• **విశ్లేషణ** — సామర్థ్య కొరత, శాఖల వారీ వివరాలు, ధోరణి, ఉద్భవిస్తున్న నైపుణ్యాలు\n"
               "• **ఒక అధికారి** — పేరు, user id, EMP ID లేదా ఇమెయిల్ ఇవ్వండి\n"
               "• **నిర్వహణ** — రిమైండర్లు, కేటాయించిన ప్రణాళికలు, సేవా స్థితి\n"
               "• **నావిగేషన్** — ఏ admin tab లేదా learner dashboard అయినా తెరవగలను"),
    },
}


def lead(key: str, variant: str, **fields: Any) -> str:
    text = _t(LEAD, key, variant)
    return text.format(**fields) if fields else text


# ── Builders ──────────────────────────────────────────────────────────────────

def _scope_text(scope: Dict[str, str], variant: str) -> str:
    if not scope:
        return label("nsoWide", variant)
    return " · ".join(scope.values())


def _scope_footer(scope: Dict[str, str], variant: str) -> str:
    if not scope:
        return ""
    return f"\n\n_{label('scopeNote', variant)}: {' · '.join(scope.values())}_"


def _pct(value: Optional[float], variant: str) -> str:
    return f"{value}%" if value is not None else label("suppressed", variant)


def _bullet(name: str, value: Any) -> str:
    return f"• **{name}:** {value}"


def _count(value: Any) -> str:
    """Small-cell counts arrive as `workforce_service.cell()` dicts
    ({value, suppressed, display}), where a group of 1–4 shows as "<5".
    Anything else is already a plain number."""
    return value["display"] if isinstance(value, dict) else str(value)


def overview(facts: Dict[str, Any], scope: Dict[str, str], variant: str) -> str:
    m = facts["mandatory"]
    lines = [
        _bullet(label("officials", variant), facts["total"]),
        _bullet(label("compliance", variant),
                label("suppressed", variant) if facts["suppressed"] else f"{facts['compliancePct']}%"),
        _bullet(label("mandatory", variant),
                f"{_pct(m['completionPct'], variant)} — {m['coursesCompleted']}/{m['coursesAssigned']}"),
        _bullet(label("behind", variant), m["behind"]),
        _bullet(label("avgMissing", variant), facts["avgMissing"]),
    ]
    return (lead("overview", variant, scope=_scope_text(scope, variant)) + "\n" + "\n".join(lines)
            + _scope_footer(scope, variant))


def officials(facts: Dict[str, Any], scope: Dict[str, str], variant: str) -> str:
    lines = [
        _bullet(label("officials", variant), facts["total"]),
        _bullet(label("compliant", variant), facts["compliant"]),
        _bullet(label("inProgress", variant), facts["inProgress"]),
        _bullet(label("required", variant), facts["required"]),
    ]
    return (lead("officials", variant, scope=_scope_text(scope, variant)) + "\n" + "\n".join(lines)
            + _scope_footer(scope, variant))


def compliance(facts: Dict[str, Any], scope: Dict[str, str], variant: str) -> str:
    lines = [
        _bullet(label("compliance", variant),
                label("suppressed", variant) if facts["suppressed"] else f"{facts['compliancePct']}%"),
        _bullet(label("compliant", variant), f"{facts['compliant']} / {facts['total']}"),
        _bullet(label("required", variant), facts["required"]),
    ]
    return (lead("compliance", variant, scope=_scope_text(scope, variant)) + "\n" + "\n".join(lines)
            + _scope_footer(scope, variant))


def mandatory(facts: Dict[str, Any], behind_rows: List[Dict[str, Any]],
              scope: Dict[str, str], variant: str) -> str:
    m = facts["mandatory"]
    lines = [
        _bullet(label("mandatory", variant), _pct(m["completionPct"], variant)),
        _bullet(label("completedCourses", variant), f"{m['coursesCompleted']} / {m['coursesAssigned']}"),
        _bullet(label("behind", variant), f"{m['behind']} / {m['officialsWithPlan']}"),
    ]
    for row in behind_rows:
        lines.append(f"  · {row['name']} ({row['govId']}) — {row['completed']}/{row['total']}")
    return (lead("mandatory", variant, scope=_scope_text(scope, variant)) + "\n" + "\n".join(lines)
            + _scope_footer(scope, variant))


def departments(rows: List[Dict[str, Any]], scope: Dict[str, str], variant: str) -> str:
    lines = [
        f"• **{r['dept']}** — {r['headcount']} {label('officials', variant).lower()}, "
        f"{_pct(r['pct'], variant)} {label('compliant', variant).lower()}, "
        f"{label('mandatory', variant)} {_pct(r['mandatoryPct'], variant)}"
        for r in rows
    ]
    return (lead("departments", variant, scope=_scope_text(scope, variant)) + "\n"
            + ("\n".join(lines) or f"• {label('none', variant)}") + _scope_footer(scope, variant))


def shortages(rows: List[Dict[str, Any]], scope: Dict[str, str], variant: str) -> str:
    lines = [f"• **{r['competency']}** — {label('shortage', variant)} {r['gap']}, "
             f"{_count(r['officials'])} {label('officials', variant).lower()}" for r in rows]
    return (lead("shortages", variant, scope=_scope_text(scope, variant)) + "\n"
            + ("\n".join(lines) or f"• {label('none', variant)}") + _scope_footer(scope, variant))


def emerging(items: List[Dict[str, Any]], horizon: int, scope: Dict[str, str], variant: str) -> str:
    lines = []
    for item in items:
        lines.append(
            f"{item['rank']}. **{item['competencyName']}** — {label('priority', variant)} "
            f"{item['priorityScore']}, {_count(item['supplyNow'])} → "
            f"{_count(item['expectedSupply36'])} / {_count(item['required'])}"
            f"\n   _{label('action', variant)}: {item['recommendedAction']}_")
    return (lead("emerging", variant, scope=_scope_text(scope, variant), horizon=horizon) + "\n"
            + ("\n".join(lines) or f"• {label('none', variant)}") + _scope_footer(scope, variant))


def trends(facts: Dict[str, Any], scope: Dict[str, str], variant: str) -> str:
    arrow = {"up": "▲", "down": "▼", "flat": "▬"}[facts["direction"]]
    lines = [
        _bullet(label("trained12m", variant),
                f"{facts['firstPct']}% → {facts['lastPct']}%  {arrow} {facts['delta']:+}"),
    ]
    if facts.get("mandatoryPct") is not None:
        lines.append(_bullet(label("mandatory", variant), f"{facts['mandatoryPct']}%"))
    if facts.get("weeklyAvg") is not None:
        lines.append(_bullet(label("weekly", variant), facts["weeklyAvg"]))
    if facts.get("avgLevel") is not None:
        lines.append(_bullet(label("avgLevel", variant), facts["avgLevel"]))
    if facts.get("atTargetPct") is not None:
        lines.append(_bullet(label("atTarget", variant), f"{facts['atTargetPct']}%"))
    return (lead("trends", variant, scope=_scope_text(scope, variant),
                 first=facts["firstDate"], last=facts["lastDate"])
            + "\n" + "\n".join(lines) + _scope_footer(scope, variant))


_HEALTH_ICON = {"ok": "🟢", "degraded": "🟡", "down": "🔴", "unknown": "⚪"}


def health(payload: Dict[str, Any], variant: str) -> str:
    lines = [f"{_HEALTH_ICON.get(c['status'], '⚪')} **{c['label']}** — {c['detail']}"
             for c in payload.get("components", [])]
    return lead("health", variant, overall=payload.get("overall", "unknown"),
                checked=(payload.get("checkedAt") or "")[:16]) + "\n" + "\n".join(lines)


def nudges(count: int, rows: List[Dict[str, Any]], variant: str) -> str:
    lines = [f"• **{r['name']}** — {(r.get('createdAt') or '')[:10]}"
             f"{'' if r.get('readAt') else ' (unread)'}" for r in rows]
    return lead("nudges", variant, count=count) + "\n" + ("\n".join(lines) or f"• {label('none', variant)}")


def assignments(count: int, rows: List[Dict[str, Any]], variant: str) -> str:
    lines = [f"• **{r['title']}** — {r['assignees']} {label('officials', variant).lower()}, "
             f"{r['progress']['completionPct']}%{' ⚠️' if r.get('overdue') else ''}" for r in rows]
    return lead("assignments", variant, count=count) + "\n" + ("\n".join(lines) or f"• {label('none', variant)}")


def needs_training(count: int, rows: List[Dict[str, Any]], scope: Dict[str, str], variant: str) -> str:
    lines = [f"• **{r['name']}** ({r['govId']}) — {r['department']}, "
             f"{r['missingCount']} {label('skillGaps', variant).lower()}" for r in rows]
    return (lead("needsTraining", variant, count=count, scope=_scope_text(scope, variant)) + "\n"
            + ("\n".join(lines) or f"• {label('none', variant)}") + _scope_footer(scope, variant))


def official(facts: Dict[str, Any], variant: str) -> str:
    lines = [
        _bullet(label("designation", variant), facts["designation"]),
        _bullet(label("department", variant), facts["department"]),
        _bullet(label("grade", variant), facts["gradeLabel"]),
        _bullet(label("office", variant), facts["officeName"]),
        _bullet(label("status", variant), facts["statusLabel"]),
        _bullet(label("completedCourses", variant), facts["completedCourses"]),
    ]
    if facts.get("mandatoryTotal"):
        pending = ", ".join(facts["pendingCourses"]) or label("none", variant)
        lines.append(_bullet(label("mandatory", variant),
                             f"{facts['mandatoryCompleted']}/{facts['mandatoryTotal']} ({facts['mandatoryCycle']})"))
        lines.append(_bullet(label("pending", variant), pending))
    if facts.get("karmaPoints") is not None:
        lines.append(_bullet(label("karma", variant), facts["karmaPoints"]))
    if facts.get("nudgeCount"):
        lines.append(_bullet(label("nudges", variant),
                             f"{facts['nudgeCount']} (last {facts.get('lastNudgedAt') or '—'})"))
    if facts.get("assignedPlans"):
        lines.append(_bullet(label("plans", variant),
                             f"{facts['assignedPlans']} — {', '.join(facts.get('assignedPlanTitles') or [])}"))

    if facts["gaps"]:
        lines.append("")
        lines.append(f"**{label('skillGaps', variant)}** ({facts['gapCount']}):")
        lines += [f"• {g['name']} — {label('level', variant)} {g['level']} / "
                  f"{label('target', variant)} {g['target']}" for g in facts["gaps"]]
    elif facts["snapshotReady"] and facts["assessedCount"]:
        lines.append(_bullet(label("skillGaps", variant), label("none", variant)))

    return lead("userFound", variant, name=facts["name"], govId=facts["govId"],
                userId=facts["userId"]) + "\n" + "\n".join(lines)


def ambiguous(term: str, rows: List[Dict[str, Any]], variant: str) -> str:
    lines = [f"• **{r['firstName']} {r['lastName']}** — {r['govId']} · {r['department']}" for r in rows]
    return lead("userAmbiguous", variant, term=term, count=len(rows)) + "\n" + "\n".join(lines)


def not_found(term: str, variant: str) -> str:
    return lead("userNotFound", variant, term=term)


def navigation(label_text: str, variant: str) -> str:
    return lead("nav", variant, label=label_text)


def error(detail: str, variant: str) -> str:
    return lead("error", variant, detail=detail)
