"""Gyan reply templates — Hinglish (romanized Hindi). Strings only; see services/chat_messages/__init__.py."""

T = {
    'greeting.home': (
        'Namaste! 🙏 Main **Gyan** hoon — MoSPI ka AI Assistant.\n'
        '\n'
        'Main aapko yeh platform samajhne mein madad kar sakta hoon:\n'
        '• Platform ke features aur sections ke baare mein\n'
        '• MoSPI aur iGOT Karmayogi ke baare mein\n'
        '• Login karne mein guide karna\n'
        '• Kisi bhi section par le jaana\n'
        '\n'
        'Aaj main aapki kya madad kar sakta hoon? 🎓'
    ),
    'user_identity.home': (
        '🔐 Aapka naam aur employee ID dekhne ke liye **login karna hoga**.\n'
        '\n'
        'Page ke top par **Official Login** button click karein — ya main aapke liye login dialog khol sakta hoon.'
    ),
    'profile_stats.home': (
        '🔐 Aapki profile stats **login karne ke baad** hi dikhti hain.\n'
        '\n'
        'Page ke top par **Official Login** button click karein.'
    ),
    'skill_gaps.home': (
        '🔐 Aapke skill gaps **login karne ke baad** dikhenge.\n'
        '\n'
        'Page ke top par **Official Login** button click karein.'
    ),
    'concept_skill_gap': (
        '**Skill Gap** ka matlab hai — aapke **current competency level** aur \n'
        'aapki job role ke liye **required (target) level** ke beech ka antar.\n'
        '\n'
        '**Example:**\n'
        "Maan lijiye 'Strategic Thinking' competency mein:\n"
        '• Aapka current level: **Level 1** (beginner)\n'
        '• Aapki Deputy Director role ke liye zaruri: **Level 4** (expert)\n'
        '• **Gap Score = 3** — matlab aapko 3 levels aur improve karna hai\n'
        '\n'
        '**Competency Levels (FRAC framework):**\n'
        '• Level 1 — Awareness (basic knowledge)\n'
        '• Level 2 — Foundational (can apply with guidance)\n'
        '• Level 3 — Practitioner (independent application)\n'
        '• Level 4 — Expert (guides others, sets policy)\n'
        '\n'
        'Aapke Dashboard par **Competency & Skill-Gap Analysis** card mein \n'
        'har skill ka current level (pip dots) aur target level dikh ta hai. 📊'
    ),
    'last_assessment': (
        'Aapki **last assessment date** Profile Header mein dikhti hai — jo har tab ke top par hoti hai.\n'
        '\n'
        "📅 **Clock icon** ke paas, 'Last assessed: DD Mon YYYY' format mein date dikhti hai.\n"
        '\n'
        'Detailed assessment history aur quiz scores dekhne ke liye **Progress tab** par jayein (top navbar mein TrendingUp icon). Wahan aapki achievements timeline hoti hai jisme:\n'
        '• RAG Quiz results (score % ke saath)\n'
        '• External Certifications\n'
        '• Date aur title har achievement ka'
    ),
    'achievements': (
        'Aapki achievements **Progress tab** par dekhne ko milti hain.\n'
        '\n'
        '**Progress tab** kaise open karein:\n'
        '1. Top navigation bar mein **TrendingUp icon** par click karein\n'
        "2. 'Progress' button choose karein (teen tabs mein se)\n"
        '\n'
        'Wahan aapko milega:\n'
        '📊 **Competency Radar Chart** — sab skills ka Current vs Target level\n'
        '🏆 **Recent Achievements** — RAG Quiz results aur External Certifications\n'
        '\n'
        'Har achievement mein date, title aur score (%) show hota hai.'
    ),
    'navigation_dashboard': (
        '**Dashboard tab** kaise access karein:\n'
        '\n'
        "Top navigation bar mein **LayoutDashboard icon** ke saath **'Dashboard'** button par click karein.\n"
        '\n'
        'Dashboard tab par yeh sections milte hain:\n'
        '\n'
        '📋 **Competency & Skill-Gap Analysis** (main left panel)\n'
        '   Aapke har skill ka current level (pip-strip) aur target level,\n'
        '   domain badge (Statistical/Technical/Governance/Leadership),\n'
        '   aur gap score dikhta hai.\n'
        '\n'
        '📊 **Learning Snapshot** (right panel)\n'
        '   4 quick stats: Total Competencies, Active Gaps, Mandatory Gaps, Recommendations.\n'
        '\n'
        '🤖 **AI Assessment Generator** (right panel, neeche)\n'
        '   PDF ya text upload karke quiz generate karein.\n'
        '\n'
        '✨ **AI Recommended Learning Pathway** (sabse neeche)\n'
        '   Aapke gaps ke basis par personalized course cards.'
    ),
    'navigation_my_courses': (
        '**My Courses tab** kahan hai aur kaise access karein:\n'
        '\n'
        "Top navigation bar mein **BookOpen icon** ke saath **'My Courses'** button par click karein.\n"
        '\n'
        'My Courses tab mein dikhta hai:\n'
        '\n'
        '📚 **Active Enrollments** — aapke enrolled sabhi courses\n'
        '   Har course card mein:\n'
        '   • Course naam aur source (iGOT Karmayogi / Other)\n'
        '   • **Course Progress bar** (% complete)\n'
        '   • Remaining hours\n'
        '   • Last accessed date\n'
        "   • **'Continue'** button (course resume karne ke liye)\n"
        '\n'
        'Agar koi enrolled course nahi hai, toh **Dashboard tab** par jayein\n'
        "aur 'AI Recommended Learning Pathway' se course select karein."
    ),
    'navigation_progress': (
        '**Progress tab** kahan hai aur kya dikhta hai:\n'
        '\n'
        "Top navigation bar mein **TrendingUp icon** ke saath **'Progress'** button par click karein.\n"
        '\n'
        'Progress tab mein do sections hain:\n'
        '\n'
        '📊 **Competency Radar Chart** (left side)\n'
        '   Aapke sabhi skills ka radar/spider chart — blue fill = Current level,\n'
        '   dashed line = Target level. Kisi bhi skill par hover karein\n'
        '   toh Current/Target values aur gap tooltip mein dikh ta hai.\n'
        '\n'
        '🏆 **Recent Achievements** (right side)\n'
        '   Timeline format mein — RAG Quiz results (score %) aur\n'
        '   External Certifications, date ke saath.'
    ),
    'navigation_ai_quiz': (
        '**AI Assessment Generator** kaise use karein:\n'
        '\n'
        'Yeh feature **Dashboard tab** par right panel mein neeche dikhta hai.\n'
        '\n'
        'Steps:\n'
        '1. **Dashboard tab** par jayein (top navbar → Dashboard icon)\n'
        "2. Right side pe **'AI Assessment Generator'** card dhundhein\n"
        "   (Bot icon ke saath, subtitle: 'RAG Document-to-Quiz Pipeline')\n"
        '3. Text box mein apna query/topic type karein\n'
        "4. (Optional) **'Attach document'** par click karke\n"
        '   .pdf / .pptx / .txt file attach karein\n'
        "5. **'Generate Assessment'** button click karein\n"
        '\n'
        '💡 File upload se zyada accurate MCQs milte hain kyunki\n'
        'AI document ke content se questions banata hai.'
    ),
    'navigation_profile': (
        '**Profile, Password aur Logout** kaise karein:\n'
        '\n'
        'Top navigation bar mein **right side** par yeh options hain:\n'
        '\n'
        '🔒 **Change Password** — Lock icon par click karein\n'
        "   → '/change-password' page par le jaata hai\n"
        '\n'
        "🚪 **Sign Out** — 'Sign Out' button par click karein\n"
        '   → aap login page par wapas aa jayenge\n'
        '\n'
        '🌙/☀️ **Dark/Light Mode** — Moon ya Sun icon par click karein\n'
        '\n'
        '🏠 **Landing Page** — Home icon par click karein\n'
        '\n'
        '📋 **Aapka Profile** (read-only) har tab ke top par dikhta hai:\n'
        '   Name, role, department, Profile ID, aur last assessment date.'
    ),
    'about_platform': (
        '**MoSPI Skill Intelligence Platform** — aapka AI-powered learning tool hai MoSPI ke government officials ke liye.\n'
        '\n'
        '🎯 **Yeh platform kya karta hai:**\n'
        '• Aapki **skill gaps** identify karta hai — job role ke liye kaunsi competencies target se kam hain\n'
        '• **Personalized courses** recommend karta hai jo aapke gaps close karein\n'
        '• **AI Assessment Generator** — PDF/PPTX upload karein, automatic MCQ quiz banega\n'
        '• **Gyan AI Chatbot** (main hoon!) — training, statistics, platform navigation ke sawal ka jawab\n'
        '\n'
        '📌 **Tabs:**\n'
        '• **Dashboard** — skill gaps + recommended courses + quiz generator\n'
        '• **My Courses** — active enrollments aur course progress\n'
        '• **Progress** — competency radar chart aur achievements\n'
        '\n'
        'Yeh platform iGOT Karmayogi ke FRAC framework se aligned hai — Mission Karmayogi ka hissa. 🇮🇳'
    ),
    'about_mospi': (
        '**MoSPI (Ministry of Statistics and Programme Implementation)** — Bharat Sarkar ka apex statistical body hai.\n'
        '\n'
        '📊 **MoSPI ke kaam:**\n'
        '• **GDP, CPI, IIP, WPI** jaise national statistics compile karna\n'
        '• **NSO** (National Statistical Office) ko supervise karna\n'
        '• Large surveys: **PLFS** (Labour Force), **HCES** (Household Consumer Expenditure)\n'
        '• **SDG India Index** — UN Sustainable Development Goals ka tracking\n'
        '\n'
        '🎓 **iGOT Karmayogi** — Mission Karmayogi ke under training platform:\n'
        '• Government officials ki capacity building\n'
        '• **FRAC framework** (Roles, Activities, Competencies) par based\n'
        '• Yeh platform us training journey ka AI-powered hissa hai 🇮🇳'
    ),
    'statistics_gdp': (
        '**GDP (सकल घरेलू उत्पाद)** — NSO dwara SNA 2008 ke anusar compute ki jati hai.\n'
        '\n'
        'Teen methods:\n'
        '• **Vyay Vidhi**: C + I + G + (X−M)\n'
        '• **Utpadan Vidhi**: GVA across industries + taxes − subsidies\n'
        '• **Aay Vidhi**: Shramik parishram + operating surplus\n'
        '\n'
        'Base year: **2011-12**. Quarterly estimates aati hain. NSO MoSPI ke under hai. 🇮🇳'
    ),
    'statistics_cpi': (
        '**CPI (उपभोक्ता मूल्य सूचकांक)** — households dwara kharide goods/services ki average price change.\n'
        '\n'
        '• Monthly NSO release, base year 2012\n'
        '• **Laspeyres formula** use hoti hai\n'
        '• 299 items, 6 groups: Food, Fuel, Housing, etc.\n'
        '• RBI inflation target: **4% ± 2%**'
    ),
    'statistics_sampling': (
        '**Sampling (प्रतिदर्श)** — puri population ka chota hissa chunke anuman lagana.\n'
        '\n'
        'NSSO mein upyog hone wale types:\n'
        '• **Stratified**: Urban/rural, state ke hisab se\n'
        '• **Cluster**: Pehle groups chunte hain (gaon/blocks)\n'
        '• **Multi-stage**: PLFS, HCES mein — district → block → ghar\n'
        '\n'
        'NSSO **rotating panel design** use karta hai time-series tracking ke liye.'
    ),
    'statistics_frac': (
        '**FRAC** — GoI ka civil servants ke liye competency framework, iGOT Karmayogi par.\n'
        '\n'
        '• **Roles**: Job positions\n'
        '• **Activities**: Role mein key functions\n'
        '• **Competencies**: Behavioural (B), Domain (D), Functional (F)\n'
        '\n'
        'Is platform ka skill gap assessment FRAC dictionary se aligned hai. 📋'
    ),
    'out_of_scope': (
        'Yeh sawaal meri knowledge ke bahar hai. 🙏\n'
        '\n'
        'Main ek **MoSPI training assistant** hoon — main sirf government statistical training, skill gaps, courses, aur platform navigation ke baare mein baat kar sakta hoon.\n'
        '\n'
        'Kya aap apne training se related kuch poochna chahte hain?'
    ),
    'farewell': 'Alvida! 🙏 Aapki learning mein safalta ki shubhkamanayein. **Jai Hind!** 🇮🇳',
    'fallback.home': (
        'Maafi chahta hoon, main is sawaal ka jawab nahi de sakta. 🙏\n'
        '\n'
        'Main madad kar sakta hoon:\n'
        '• Platform features ke baare mein\n'
        '• MoSPI / iGOT ke baare mein\n'
        '• Login karne mein\n'
        '• Kisi section par scroll karne mein\n'
        '\n'
        'Kuch aur poochna chahte hain?'
    ),
    'fallback.dashboard': (
        'Main is sawaal ka jawab nahi de sakta. 🙏\n'
        '\n'
        'Main madad kar sakta hoon:\n'
        '• Skill gaps aur competency analysis\n'
        '• Course recommendations\n'
        '• Platform navigation (Dashboard, My Courses, Progress)\n'
        '• Statistics topics (GDP, CPI, FRAC, Sampling)\n'
        '\n'
        'Kya aap inmein se kuch poochhna chahte hain?'
    ),
    'greeting.dashboard': (
        "Namaste! 🙏 Main **Gyan** hoon — aapka MoSPI AI Training Assistant.\n\n"
        "Main dekh sakta hoon ki aap **{role}** hain **{dept}** mein.\n"
        "Aapke paas **{gap_count} active skill gap(s)** hain.\n\n"
        "Aap mujhse pooch sakte hain:\n"
        "• Apne skill gaps ke baare mein\n"
        "• Recommended courses ke baare mein\n"
        "• Platform navigate karne mein madad\n"
        "• Statistics topics (GDP, CPI, Sampling, FRAC)\n\n"
        "Aaj main aapki kya madad kar sakta hoon? 🎓"
    ),
    'how_are_you': [
        "Main bilkul theek hoon! 🤖 Ek AI hoon — kabhi thakta nahi!\n\nAap batao, main aapki kya madad kar sakta hoon? 🎓",
        "Bahut acha hoon, shukriya poochne ke liye! 😄\nAapke skill gaps aur courses ke liye main hamesha taiyaar hoon.",
    ],
    'bot_identity': (
        "Main **Gyan (ज्ञान)** hoon — MoSPI ka AI Learning Assistant. 🤖\n\n"
        "Main **English, Hindi (हिंदी ya Hinglish), मराठी, বাংলা, ગુજરાતી, ଓଡ଼ିଆ, தமிழ் aur తెలుగు** samajhta hoon aur inhi mein jawab deta hoon.\n\n"
        "Main aapki madad kar sakta hoon:\n"
        "• **Skill Gaps** — aapke current aur target levels\n"
        "• **Course Recommendations** — personalized learning pathway\n"
        "• **Platform Navigation** — Dashboard, My Courses, Progress tabs\n"
        "• **Statistics** — GDP, CPI, Sampling, FRAC framework\n\n"
        "Aaj main aapki kya madad kar sakta hoon? 🎓"
    ),
    'gratitude': [
        "Khushi hui madad karke! 😄 Kya aur kuch poochna hai?",
        "Bilkul! Agar aur koi sawaal ho toh zaroor poochein. 🎓",
        "Main hamesha yahan hoon. Aur kuch chahiye? 🤖",
    ],
    'user_identity.dashboard': (
        "👤 **{name_line}**\n"
        "🪪 **{id_line}**\n"
        "🏢 **Department**: {dept}\n"
        "💼 **Job Role**: {role}\n"
        "✅ **Verified Official** badge aapke naam ke saath dikhta hai.\n\n"
        "📅 Last Assessment Date bhi Profile Header mein Clock icon ke paas dikhti hai."
    ),
    'user_identity.name_known': "Full Name: {full_name}",
    'user_identity.name_unknown': "Full Name: Profile Header mein dikhta hai (har tab ke top par)",
    'user_identity.id_known': "Gov ID / Employee ID: {gov_id}",
    'user_identity.id_unknown': "Gov ID / Employee ID: Profile Header mein dikhta hai",
    'profile_stats.dashboard': (
        "**Aapka Profile Overview** ({role}, {dept}):\n\n"
        "📊 **Learning Snapshot** (Dashboard → right panel mein dikhta hai)\n"
        "• Total Competencies Assessed: **{total}**\n"
        "• Competencies Met: **{met}**\n"
        "• Active Gaps: **{gap_count}**\n"
        "• Completion: **{completion_pct}%** — {tier_label}\n\n"
        "🎯 **Gap Detail:**\n"
        "• Sabse bada gap: **{top_skill} ({top_gap} levels)**\n"
        "• Average gap score: {avg_gap}\n"
        "• Domain-wise gaps:\n{domain_lines}\n\n"
        "Apne skill gaps detail mein dekhne ke liye **Dashboard tab** par jayein. "
        "Progress chart ke liye **Progress tab** use karein. 📈"
    ),
    'tier.on_track': "Aap sahi raaste par hain 🟢",
    'tier.needs_focus': "Kuch aur mehnat zaruri hai 🟡",
    'tier.critical': "Turant dhyan dena zaruri hai 🔴",
    'domain_line': "  • {domain}: {count} gap(s)",
    'domain_none': "  • No active gaps",
    'none': "None",
    'skill_gaps.none': "Mashallah! 🎉 Aapke **{total} competencies** sab target level par hain.\n\nAap bahut accha kar rahe hain '{role}' role mein!",
    'skill_gaps.list': (
        "Aapke current skill gaps ({role} ke liye):\n\n"
        "{gap_lines}\n\n"
        "Sabse bada gap **{top_skill}** mein hai — {top_gap} level ka farq.\n\n"
        "💡 *Yeh gaps Dashboard tab ke **Competency & Skill-Gap Analysis** card mein dikhte hain, "
        "jahan har competency ki current level aur target level pip-strip ke saath show hoti hai.*\n\n"
        "Kya main courses suggest karun is gap ko close karne ke liye?"
    ),
    'gap_line': "• **{skill}** ({domain}): Level {current} → {target} chahiye (Gap: {gap})",
    'recommend.none': "Abhi aapke liye recommendations generate nahi hui hain. Dashboard refresh karke dekhein.",
    'recommend.reason_gap': "**{top_skill}** mein {top_gap}-level gap",
    'recommend.reason_role': "aapke role requirements",
    'recommend.list': (
        "Aapke liye personalized learning pathway, {reason} ke basis par:\n\n"
        "{rec_lines}\n\n"
        "**{first_title}** se shuru karna best rahega — kyunki {first_reason}\n\n"
        "💡 *Yeh courses **Dashboard tab** ke sabse neeche '**AI Recommended Learning Pathway**' "
        "section mein dikhte hain.*"
    ),
    'rec_line': "{index}. **{title}** ({provider}, {hours}h)",
    'progress': (
        "Aapki progress summary ({role}):\n\n"
        "✅ **{met}/{total}** competencies target level par hain ({pct}%)\n"
        "⚠️ **{gap_count}** gaps abhi bhi close karne hain\n\n"
        "{encouragement}\n\n"
        "💡 *Detailed progress radar chart dekhne ke liye **Progress tab** par click karein. "
        "Wahan har skill ka Current vs Target level radar chart mein dikh ta hai, "
        "saath mein aapki recent achievements bhi.*"
    ),
    'progress.good': "Bahut badhiya! Aap sahi raaste par hain. 👏",
    'progress.keep_going': "Abhi shuru karte hain — recommended courses follow karein!",
    'motivation': (
        "Main samajhta hoon — upskilling aur kaam saath mein karna mushkil lagta hai. 💪\n\n"
        "Lekin yaad rakhein: **India ke statistical system ko aap jaise dedicated officials ki zarurat hai.** "
        "Aapka kaam GDP estimates se lekar poverty measurement tak — lakho logon ki lives affect karta hai.\n\n"
        "Ek step ek time: **sirf 30 minutes roz** — kuch hafte mein results aane lagte hain.\n"
        "Abhi start karein **{first_rec}** se! 🚀\n\n"
        "Course **Dashboard tab → AI Recommended Learning Pathway** mein milega."
    ),
    'motivation.default_course': "aapka pehla recommended course",
    'navigation_home.home': "Page ke top par le ja raha hoon! 🏠",
    'navigation_home.dashboard': "Aapko **Landing Page** par wapas le ja raha hoon! 🏠",
    'navigation_features.home': (
        "**Features** section mein 6 capabilities hain:\n"
        "AI Skill Gap Analysis, iGOT Course Mapping, RAG Document-to-Quiz, Karmayogi Sync, Air-Gapped NLP Assistant aur Analytics Dashboard.\n\n"
        "Aapko wahan le ja raha hoon! 🚀"
    ),
    'navigation_about.home': (
        "**About** section mein MoSPI ka mission, FRAC framework, iGOT integration aur security-first approach describe hai.\n\n"
        "Aapko wahan le ja raha hoon! 📖"
    ),
    'navigation_contact.home': (
        "**Contact** links — Privacy Policy, Terms aur Help & FAQ — page ke neeche footer mein hain.\n\n"
        "Aapko wahan le ja raha hoon! 📬"
    ),
    'landing_section.dashboard': (
        "**{section}** section landing page par hai. "
        "Wahan jaane ke liye top navigation bar mein **Home** icon par click karein. 🏠"
    ),
    'navigation_login.home': (
        "**Official Login** dialog khol raha hoon! 🔑\n\n"
        "Aap **Statistical Official** ke roop mein login kar sakte hain ya "
        "**Admin Portal** access kar sakte hain."
    ),
    'navigation_login.dashboard': (
        "Aap pehle se signed in hain. 🔐\n\n"
        "Account badalne ke liye navigation bar mein top-right par **Sign Out** karein, phir dobara login karein."
    ),
    'navigation_login.credentials': (
        "Main aapke liye **Official Login** dialog abhi khol raha hoon! 🔑\n\n"
        "Lekin **suraksha ke liye**, main chat ke zariye credentials enter nahi kar sakta — "
        "aapka username aur password seedha secure login form mein hi type karein.\n\n"
        "Login dialog khul raha hai — wahan seedha details type karein. 🛡️"
    ),
    'ui_action_request': (
        "Main aapke liye **Dark / Light mode** aur website ki language (**English / हिंदी**) badal sakta hoon — "
        "bas boliye, jaise *\"dark mode on karo\"* ya *\"language hindi mein karo\"*.\n\n"
        "**Font size** ke liye browser zoom use karein (**Ctrl +** / **Ctrl −**)."
    ),
    'action.theme.dark': "Ho gaya! 🌙 Main ne aapke liye **Dark Mode** switch kar diya.",
    'action.theme.light': "Ho gaya! ☀️ Main ne aapke liye **Light Mode** switch kar diya.",
    'action.theme.toggle': "Ho gaya! 🌓 Main ne theme badal diya.",
    'action.language': "Ho gaya! Main ne website ko **{language_name}** mein switch kar diya. 🇮🇳",
    'action.theme_language': "Ho gaya! ✅ **{theme_name} Mode** aur **{language_name}** language — dono switch kar diye.",
    'theme_name.dark': "Dark",
    'theme_name.light': "Light",
    'language_name.hi': "Hindi",
    'language_name.en': "English",
}
