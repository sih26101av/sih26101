from routers.chatbot import ChatRequest, RecommendationContext, SkillGapContext

GAP_NAMES = ["Survey Design", "National Accounts", "Data Visualisation"]
COURSE_TITLES = ["Foundations of Sampling Methods", "SNA 2008 in Practice", "Dashboards with Python"]


def sample_request(message: str = "hello", context: str = "dashboard") -> ChatRequest:
    return ChatRequest(
        user_id="usr_720465595",
        message=message,
        job_role="Deputy Director",
        department="NSO (Field Operations)",
        full_name="Gabriel Manda",
        gov_id="EMP-8472",
        context=context,
        skill_gaps=[
            SkillGapContext(skillName=GAP_NAMES[0], domain="Statistical", currentLevel=1, targetLevel=4, gapScore=3),
            SkillGapContext(skillName=GAP_NAMES[1], domain="Statistical", currentLevel=2, targetLevel=3, gapScore=1),
            SkillGapContext(skillName=GAP_NAMES[2], domain="Technical", currentLevel=3, targetLevel=2, gapScore=0),
            SkillGapContext(skillName="Team Leadership", domain="Leadership", currentLevel=2, targetLevel=4, gapScore=2),
        ],
        recommendations=[
            RecommendationContext(title=COURSE_TITLES[0], provider="NSSTA", durationHours=6, matchReason="Closes your Survey Design gap"),
            RecommendationContext(title=COURSE_TITLES[1], provider="iGOT Karmayogi", durationHours=4.5, matchReason="Targets National Accounts"),
            RecommendationContext(title=COURSE_TITLES[2], provider="iGOT Karmayogi", durationHours=3, matchReason="Builds technical depth"),
        ],
    )
