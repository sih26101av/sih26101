"""End-to-end /chat behaviour per language through the real multilingual classifier (loads the chat model)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.chatbot import router
from tests.fixtures import COURSE_TITLES, GAP_NAMES, sample_request

app = FastAPI()
app.include_router(router, prefix="/api/v1")
client = TestClient(app)

# Phrasings are deliberately not copied from ai/intent_corpus.
QUERIES = {
    "en": ("which competencies am I weakest in", "what training should I take next",
           "show me the courses I'm enrolled in", "please switch on dark mode"),
    "hi_latn": ("mujh mein kaunsi skills kam hain", "mujhe kaunsa course karna chahiye batao",
                "maine jin courses mein enroll kiya hai woh dikhao", "please dark mode on kar do"),
    "hi": ("मुझमें कौन से कौशल कम हैं", "मुझे कौन सा कोर्स करना चाहिए बताइए",
           "मैंने जिन कोर्स में दाखिला लिया है वो दिखाओ", "कृपया डार्क मोड चालू कीजिए"),
    "mr": ("माझ्यात कोणती कौशल्ये कमी आहेत", "मी कोणता कोर्स करावा ते सांगा",
           "मी ज्या कोर्सना प्रवेश घेतला ते दाखवा", "कृपया डार्क मोड सुरू करा"),
    "bn": ("আমার কোন দক্ষতাগুলো কম আছে", "কোন কোর্সটা আমার করা উচিত বলো",
           "আমি যে কোর্সগুলোতে ভর্তি হয়েছি সেগুলো দেখাও", "অনুগ্রহ করে ডার্ক মোড চালু করুন"),
    "gu": ("મારામાં કઈ કુશળતા ઓછી છે", "મારે કયો કોર્સ કરવો સારો રહેશે",
           "મેં જે કોર્સમાં નોંધણી કરી છે તે બતાવો", "કૃપા કરીને ડાર્ક મોડ ચાલુ કરો"),
    "or": ("ମୋ ଠାରେ କେଉଁ ଦକ୍ଷତା କମ୍ ଅଛି", "ମୋ ପାଇଁ କେଉଁ କୋର୍ସ ଭଲ ହେବ",
           "ମୁଁ ନାମ ଲେଖାଇଥିବା କୋର୍ସଗୁଡ଼ିକ ଦେଖାନ୍ତୁ", "ଦୟାକରି ଡାର୍କ ମୋଡ ଚାଲୁ କରନ୍ତୁ"),
    "ta": ("எனக்கு எந்த திறன்கள் குறைவாக உள்ளன", "நான் எந்த கோர்ஸ் படிக்கலாம் சொல்லுங்கள்",
           "நான் சேர்ந்த கோர்ஸ்களைக் காட்டுங்கள்", "தயவுசெய்து டார்க் மோடை ஆன் செய்யுங்கள்"),
    "te": ("నాకు ఏ నైపుణ్యాలు తక్కువగా ఉన్నాయి", "నేను ఏ కోర్సు చేస్తే మంచిది",
           "నేను చేరిన కోర్సులను చూపించండి", "దయచేసి డార్క్ మోడ్ ఆన్ చేయండి"),
}

# Hindi and Marathi share Devanagari; short-text detection between them is imperfect
# (measured by scripts/eval_intents.py), so either ISO code is accepted for these two.
ACCEPTED_ISO = {"en": {"en"}, "hi_latn": {"hi"}, "hi": {"hi", "mr"}, "mr": {"mr", "hi"},
                "bn": {"bn"}, "gu": {"gu"}, "or": {"or"}, "ta": {"ta"}, "te": {"te"}}


def _chat(message: str) -> dict:
    response = client.post("/api/v1/chat", json=sample_request(message, "dashboard").model_dump())
    assert response.status_code == 200
    return response.json()


@pytest.mark.parametrize("variant", QUERIES)
def test_skill_gaps(variant):
    body = _chat(QUERIES[variant][0])
    assert body["detected_language"] in ACCEPTED_ISO[variant]
    assert body["engine"] == "semantic"
    assert GAP_NAMES[0] in body["reply"]


@pytest.mark.parametrize("variant", QUERIES)
def test_recommendations(variant):
    body = _chat(QUERIES[variant][1])
    assert body["detected_language"] in ACCEPTED_ISO[variant]
    assert COURSE_TITLES[0] in body["reply"]


@pytest.mark.parametrize("variant", QUERIES)
def test_my_courses_navigation(variant):
    body = _chat(QUERIES[variant][2])
    assert body["navigate_action"] == {"type": "tab", "target": "my-courses", "label": "My Courses tab"}


@pytest.mark.parametrize("variant", QUERIES)
def test_dark_mode_action(variant):
    body = _chat(QUERIES[variant][3])
    assert body["navigate_action"]["type"] == "theme"
    assert body["navigate_action"]["target"] == "dark"


# Every learner sidebar section is reachable from chat (targets = LearnerDashboard TabType ids).
SIDEBAR_QUERIES = [
    ("open the skill gap centre", "skill-gap"),
    ("go to the recommendations tab", "recommendations"),
    ("open assessment studio", "assessments"),
    ("where do I upload my certificate", "certificates"),
    ("show my karma points", "karma"),
    ("skill gap centre kholo", "skill-gap"),
    ("असेसमेंट स्टूडियो खोलो", "assessments"),
    ("मेरे कितने कर्मा अंक हैं", "karma"),
]


@pytest.mark.parametrize("message,target", SIDEBAR_QUERIES)
def test_sidebar_section_navigation(message, target):
    action = _chat(message)["navigate_action"]
    assert action and action["type"] == "tab" and action["target"] == target


@pytest.mark.parametrize("message", ["what are my skill gaps", "recommend me a course"])
def test_questions_answer_in_chat_without_navigating(message):
    assert _chat(message)["navigate_action"] is None
