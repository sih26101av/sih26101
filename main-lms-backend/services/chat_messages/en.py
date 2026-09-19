"""Gyan reply templates — English. Strings only; see services/chat_messages/__init__.py."""

T = {
    'greeting.home': (
        "Hello! 👋 I'm **Gyan**, the MoSPI AI Assistant.\n"
        '\n'
        'I can help you explore this platform:\n'
        '• Features & capabilities of the Skill Intelligence Platform\n'
        '• About MoSPI and iGOT Karmayogi\n'
        '• How to login as an official\n'
        '• Navigate to any section\n'
        '\n'
        'What would you like to know? 🎓'
    ),
    'user_identity.home': (
        '🔐 Your personal details (name, employee ID) are only visible **after you log in**.\n'
        '\n'
        'Click the **Official Login** button at the top of the page, or I can open the login dialog for you.'
    ),
    'profile_stats.home': (
        '🔐 Your profile stats are only available **after you log in**.\n'
        '\n'
        'Click **Official Login** at the top of the page to access your personalised competency dashboard.'
    ),
    'skill_gaps.home': (
        '🔐 Your skill gaps are only visible **after you log in**.\n'
        '\n'
        'Click **Official Login** at the top of the page — your personalised competency analysis will then appear on the Dashboard.'
    ),
    'concept_skill_gap': (
        'A **Skill Gap** is the difference between your **current competency level** \n'
        'and the **required (target) level** for your job role.\n'
        '\n'
        '**Example:**\n'
        "For 'Strategic Thinking' competency:\n"
        '• Your current level: **Level 1** (beginner)\n'
        '• Required for Deputy Director: **Level 4** (expert)\n'
        '• **Gap Score = 3** — you need to improve by 3 levels\n'
        '\n'
        '**Competency Levels (FRAC framework):**\n'
        '• Level 1 — Awareness (basic knowledge)\n'
        '• Level 2 — Foundational (can apply with guidance)\n'
        '• Level 3 — Practitioner (independent application)\n'
        '• Level 4 — Expert (can guide others, shapes policy)\n'
        '\n'
        'On your **Dashboard**, the **Competency & Skill-Gap Analysis** card shows \n'
        "each skill's current level (pip dots) vs. target level visually. 📊"
    ),
    'last_assessment': (
        'Your **last assessment date** is shown in the **Profile Header** — at the top of every tab.\n'
        '\n'
        "📅 Look for the **Clock icon** — it shows 'Last assessed: DD Mon YYYY'.\n"
        '\n'
        "For detailed assessment history and quiz scores, go to the **Progress tab** (TrendingUp icon in the top navbar). There you'll find:\n"
        '• RAG Quiz results with scores (%)\n'
        '• External Certifications\n'
        '• Date and title for each achievement'
    ),
    'achievements': (
        'Your achievements are visible on the **Progress tab**.\n'
        '\n'
        '**How to get there:**\n'
        '1. Click the **TrendingUp icon** (📈) in the top navigation bar\n'
        "2. Select the **'Progress'** tab\n"
        '\n'
        "On the Progress tab you'll find:\n"
        '📊 **Competency Radar Chart** — all your skills plotted Current vs Target level\n'
        '🏆 **Recent Achievements** — RAG Quiz scores and External Certifications\n'
        '\n'
        'Each achievement shows the date, title, and your score (%).'
    ),
    'navigation_dashboard': (
        '**How to access the Dashboard tab:**\n'
        '\n'
        "Click the **'Dashboard'** button (LayoutDashboard icon) in the top navigation bar.\n"
        '\n'
        'The Dashboard tab contains:\n'
        '\n'
        '📋 **Competency & Skill-Gap Analysis** (main left panel)\n'
        '   Every skill with current level pip-strip, target level, domain badge\n'
        '   (Statistical / Technical / Governance / Leadership), and gap score.\n'
        '\n'
        '📊 **Learning Snapshot** (right panel)\n'
        '   4 quick stats: Total Competencies, Active Gaps, Mandatory Gaps, Recommendations.\n'
        '\n'
        '🤖 **AI Assessment Generator** (right panel, bottom)\n'
        '   Upload a PDF/PPTX/TXT and generate an MCQ quiz.\n'
        '\n'
        '✨ **AI Recommended Learning Pathway** (bottom of page)\n'
        '   Personalized course cards ranked by your skill gap priority.'
    ),
    'navigation_my_courses': (
        '**How to access the My Courses tab:**\n'
        '\n'
        "Click the **'My Courses'** button (BookOpen icon) in the top navigation bar.\n"
        '\n'
        "On this tab you'll see:\n"
        '\n'
        '📚 **Active Enrollments** — all your currently enrolled courses\n'
        '   Each course card shows:\n'
        '   • Course title and source (iGOT Karmayogi / Other)\n'
        '   • **Course Progress bar** (% complete)\n'
        '   • Remaining hours\n'
        '   • Last accessed date\n'
        "   • **'Continue'** button to resume the course\n"
        '\n'
        "If you have no active enrollments, go to the **Dashboard tab** and pick a course from the 'AI Recommended Learning Pathway' section."
    ),
    'navigation_progress': (
        '**How to access the Progress tab:**\n'
        '\n'
        "Click the **'Progress'** button (TrendingUp icon) in the top navigation bar.\n"
        '\n'
        'The Progress tab has two sections:\n'
        '\n'
        '📊 **Competency Radar Chart** (left panel)\n'
        '   A spider chart of all your skills — blue fill = Current level,    dashed = Target level. Hover over any skill to see Current/Target values and gap.\n'
        '\n'
        '🏆 **Recent Achievements** (right panel)\n'
        '   A timeline of your RAG Quiz results (with scores) and External Certifications.'
    ),
    'navigation_ai_quiz': (
        "**Assessment Studio** 🤖 — in the left sidebar.\n"
        "\n"
        "There you can:\n"
        "• Upload a PDF, DOCX, PPTX or TXT file, or a video, audio file or YouTube link\n"
        "• Generate an AI quiz from it — passing it adds evidence to your competency levels\n"
        "• Use **Learning Mode** to study the material with Gyan first"
    ),
    'navigation_profile': (
        '**Profile, Password & Navigation options:**\n'
        '\n'
        'All these are in the **top-right of the navigation bar**:\n'
        '\n'
        '🔒 **Change Password** — click the Lock icon\n'
        '   → Takes you to the Change Password page\n'
        '\n'
        "🚪 **Sign Out** — click the 'Sign Out' button\n"
        '   → Logs you out and redirects to the login page\n'
        '\n'
        '🌙/☀️ **Dark / Light Mode** — click the Moon or Sun icon to toggle theme\n'
        '\n'
        '🏠 **Landing Page** — click the Home icon to go back to the landing page\n'
        '\n'
        '📋 **Your Profile** (read-only) is always visible at the top of each tab:\n'
        '   Shows your name, job role, department, Profile ID, and last assessment date.'
    ),
    'about_platform': (
        '**MoSPI Skill Intelligence Platform** is an AI-powered learning tool for government statistical officials.\n'
        '\n'
        '🎯 **What this platform does:**\n'
        '• Identifies your **skill gaps** — which competencies are below target for your job role\n'
        '• Recommends **personalized courses** from iGOT Karmayogi to close those gaps\n'
        '• **AI Assessment Generator** — upload any PDF/PPTX and get instant MCQ quizzes\n'
        "• **Gyan AI Chatbot** (that's me!) — answers questions about training, statistics, and navigation\n"
        '\n'
        '📌 **Three tabs:**\n'
        '• **Dashboard** — skill gaps + AI-recommended courses + quiz generator\n'
        '• **My Courses** — active enrollments and progress tracking\n'
        '• **Progress** — competency radar chart and achievement history\n'
        '\n'
        'Built for **Mission Karmayogi**, aligned with the iGOT FRAC competency framework. 🇮🇳'
    ),
    'about_mospi': (
        "**MoSPI (Ministry of Statistics and Programme Implementation)** is India's apex body for the national statistical system.\n"
        '\n'
        '📊 **What MoSPI does:**\n'
        '• Compiles national statistics: **GDP, CPI, IIP, WPI**\n'
        '• Oversees the **NSO** (National Statistical Office)\n'
        '• Conducts large-scale surveys: **PLFS** (Labour Force), **HCES** (Consumer Expenditure)\n'
        "• Tracks India's progress on the **SDG India Index**\n"
        '\n'
        '🎓 **iGOT Karmayogi** — the learning platform under **Mission Karmayogi**:\n'
        '• National capacity building for civil servants\n'
        '• Based on the **FRAC framework** (Roles, Activities, Competencies)\n'
        '• This platform is an AI-powered extension of that journey 🇮🇳'
    ),
    'statistics_gdp': (
        '**GDP (Gross Domestic Product)** in India is compiled by the National Statistical Office (NSO) following the **System of National Accounts 2008 (SNA 2008)**.\n'
        '\n'
        'Three approaches:\n'
        '• **Expenditure method**: C + I + G + (X−M)\n'
        '• **Production method**: Sum of GVA across industries + taxes − subsidies\n'
        '• **Income method**: Compensation of employees + gross operating surplus\n'
        '\n'
        'India releases GDP quarterly, with two advance estimates. Base year: **2011-12**.\n'
        '\n'
        'Key agency: NSO under MoSPI. 🇮🇳'
    ),
    'statistics_cpi': (
        '**CPI (Consumer Price Index)** measures average price changes for a basket of goods and services bought by households.\n'
        '\n'
        'In India:\n'
        '• **CPI-Combined**: Released monthly by MoSPI/NSO (base year 2012)\n'
        '• **Laspeyres formula** (fixed base-period weights)\n'
        '• Covers **299 items** across 6 groups: Food, Fuel, Housing, Clothing, Miscellaneous\n'
        '• Used by RBI as the **inflation targeting benchmark** (target: 4% ± 2%)'
    ),
    'statistics_sampling': (
        '**Sampling in official statistics** — selecting a subset to estimate population parameters.\n'
        '\n'
        'Key types used in NSSO surveys:\n'
        '• **Stratified Sampling**: Population divided into strata (urban/rural, states)\n'
        '• **Cluster Sampling**: Groups (villages/blocks) selected first\n'
        '• **Multi-stage Sampling**: Used in PLFS, HCES — districts → blocks → households\n'
        '\n'
        'NSSO uses a **rotating panel design** for many surveys to track changes over time.'
    ),
    'statistics_frac': (
        "**FRAC (Framework for Roles, Activities and Competencies)** is the Government of India's competency architecture for civil servants on iGOT Karmayogi.\n"
        '\n'
        'FRAC defines:\n'
        '• **Roles**: Job positions (Deputy Director, Field Investigator, etc.)\n'
        '• **Activities**: Key functions performed in a role\n'
        '• **Competencies**: Skills grouped as Behavioural (B), Domain (D), Functional (F)\n'
        '\n'
        'Your skill gap assessment here is **fully aligned with the FRAC dictionary**. 📋'
    ),
    'out_of_scope': (
        "That's outside my area of knowledge. 🤔\n"
        '\n'
        "I'm a **MoSPI training assistant** — I can only help with government statistical training, skill gaps, courses, and platform navigation.\n"
        '\n'
        'Is there something training-related I can help you with?'
    ),
    'farewell': 'Goodbye! 👋 Best of luck with your learning journey. **Jai Hind!** 🇮🇳',
    'fallback.home': (
        "I'm not sure I have an answer for that. 🤔\n"
        '\n'
        'On this page I can help with:\n'
        '• Platform features and capabilities\n'
        '• About MoSPI and iGOT Karmayogi\n'
        '• How to login as an official\n'
        '• Scrolling to any section\n'
        '\n'
        'Try: *"show me features"* or *"how do I login?"*'
    ),
    'fallback.dashboard': (
        "I'm not sure I understand that. 🤔\n"
        '\n'
        'I can help with:\n'
        '• Your skill gaps and competency levels\n'
        '• Course recommendations and learning pathway\n'
        '• Platform navigation (Dashboard, My Courses, Progress)\n'
        '• Statistics concepts (GDP, CPI, FRAC, Sampling)\n'
        '\n'
        'Try: *"What are my skill gaps?"* or *"take me to My Courses"*'
    ),
    'greeting.dashboard': (
        "Hello! 👋 I'm **Gyan**, your MoSPI AI Training Assistant.\n\n"
        "You're a **{role}** in {dept}. "
        "You currently have **{gap_count} active skill gap(s)**.\n\n"
        "Ask me about:\n"
        "• Your skill gaps and priority areas\n"
        "• Which courses to take next\n"
        "• How to navigate different parts of this platform\n"
        "• Statistical concepts (GDP, CPI, Sampling, FRAC)\n\n"
        "How can I help you today? 🎓"
    ),
    'how_are_you': [
        "I'm doing great, thanks for asking! 🤖 I'm an AI — I never get tired!\n\nHow can I help you today? 🎓",
        "All systems running smoothly! 😊\nReady to help you with your skill gaps, courses, or anything else.",
    ],
    'bot_identity': (
        "I'm **Gyan (ज्ञान)** — the AI Learning Assistant for MoSPI. 🤖\n\n"
        "I understand and reply in **English, हिंदी (Hindi or Hinglish), मराठी, বাংলা, ગુજરાતી, ଓଡ଼ିଆ, தமிழ் and తెలుగు**.\n\n"
        "I can help you with:\n"
        "• **Skill Gaps** — your current vs target competency levels\n"
        "• **Course Recommendations** — your personalized learning pathway\n"
        "• **Platform Navigation** — Dashboard, My Courses, Progress tabs\n"
        "• **Statistics** — GDP, CPI, Sampling, FRAC framework\n\n"
        "What can I help you with today? 🎓"
    ),
    'gratitude': [
        "Glad I could help! 😄 Anything else you'd like to know?",
        "You're welcome! Feel free to ask me anything else. 🎓",
        "Happy to assist! Is there anything else I can help with? 🤖",
    ],
    'user_identity.dashboard': (
        "👤 **{name_line}**\n"
        "🪪 **{id_line}**\n"
        "🏢 **Department**: {dept}\n"
        "💼 **Job Role**: {role}\n"
        "✅ **Verified Official** - you have a verified government official badge.\n\n"
        "📅 Your last assessment date is also shown in the Profile Header next to the Clock icon."
    ),
    'user_identity.name_known': "Full Name: {full_name}",
    'user_identity.name_unknown': "Full Name: shown in Profile Header (top of every tab)",
    'user_identity.id_known': "Gov ID / Employee ID: {gov_id}",
    'user_identity.id_unknown': "Gov ID / Employee ID: shown in Profile Header",
    'profile_stats.dashboard': (
        "**Your Profile Overview** ({role}, {dept}):\n\n"
        "📊 **Learning Snapshot** (visible on Dashboard → right panel)\n"
        "• Total Competencies Assessed: **{total}**\n"
        "• Competencies Met: **{met}**\n"
        "• Active Gaps: **{gap_count}**\n"
        "• Completion: **{completion_pct}%** — {tier_label}\n\n"
        "🎯 **Gap Summary:**\n"
        "• Biggest gap: **{top_skill} ({top_gap} level(s) behind)**\n"
        "• Average gap score: {avg_gap}\n"
        "• Gaps by domain:\n{domain_lines}\n\n"
        "Go to the **Dashboard tab** for detailed skill gap cards. "
        "Visit the **Progress tab** for your Competency Radar chart. 📈"
    ),
    'tier.on_track': "On Track 🟢",
    'tier.needs_focus': "Needs Focus 🟡",
    'tier.critical': "Critical — Act Now 🔴",
    'domain_line': "  • {domain}: {count} gap(s)",
    'domain_none': "  • No active gaps",
    'none': "None",
    'skill_gaps.none': "Excellent! 🎉 All **{total} competencies** are at or above target level for your role as {role}. Keep it up!",
    'skill_gaps.list': (
        "Here are your active skill gaps for **{role}**:\n\n"
        "{gap_lines}\n\n"
        "Your biggest priority is **{top_skill}** with a {top_gap}-level gap.\n\n"
        "💡 *You can see these visually on the **Dashboard tab** → "
        "'Competency & Skill-Gap Analysis' card (left panel). "
        "Each skill shows current level pips vs target level.*\n\n"
        "Want me to recommend courses to close this gap?"
    ),
    'gap_line': "• **{skill}** ({domain}): Level {current} → {target} needed (Gap: {gap})",
    'recommend.none': "No recommendations found yet. Try refreshing your dashboard.",
    'recommend.reason_gap': "your {top_gap}-level gap in **{top_skill}**",
    'recommend.reason_role': "your role requirements",
    'recommend.list': (
        "Based on {reason}, here's your personalized learning pathway:\n\n"
        "{rec_lines}\n\n"
        "Start with **{first_title}** — {first_reason}\n\n"
        "💡 *Find all these courses at the bottom of the **Dashboard tab**, "
        "in the '**AI Recommended Learning Pathway**' section.*"
    ),
    'rec_line': "{index}. **{title}** — {provider} | {hours}h",
    'progress': (
        "Your learning progress as **{role}**:\n\n"
        "✅ **{met}/{total}** competencies at target level ({pct}% complete)\n"
        "⚠️ **{gap_count}** gap(s) still to close\n\n"
        "{encouragement}\n\n"
        "💡 *For a detailed radar chart of all your skills (Current vs Target), "
        "switch to the **Progress tab** (TrendingUp icon in the top navbar). "
        "You'll also see your quiz and certification achievements there.*"
    ),
    'progress.good': "Great progress! You are well on track. 👏",
    'progress.keep_going': "Keep going — follow your recommended courses to close the remaining gaps!",
    'motivation': (
        "I understand — balancing work and upskilling is genuinely challenging. 💪\n\n"
        "Remember: **India's statistical system depends on dedicated officials like you.** "
        "Your data — from GDP estimates to poverty measurement — impacts millions of lives.\n\n"
        "Just **30 minutes a day** will show results within weeks. "
        "Start with **{first_rec}**! 🚀\n\n"
        "Find it on the **Dashboard tab → AI Recommended Learning Pathway** section."
    ),
    'motivation.default_course': "your first recommended course",
    'navigation_home.home': "Scrolling back to the **top** of the page! 🏠",
    'navigation_home.dashboard': "Taking you back to the **Landing Page**! 🏠",
    'navigation_features.home': (
        "The **Features** section covers all 6 capabilities:\n"
        "AI-Driven Skill Gap Analysis, Intelligent iGOT Course Mapping, Automated RAG Document-to-Quiz, "
        "Real-Time Karmayogi Synchronization, Air-Gapped NLP Assistant, and Ministry-Wide Analytics Dashboard.\n\n"
        "Scrolling you there now! 🚀"
    ),
    'navigation_about.home': (
        "The **About** section describes MoSPI's mission, the FRAC-aligned framework, "
        "iGOT integration, and our security-first approach.\n\nScrolling you there now! 📖"
    ),
    'navigation_contact.home': (
        "The **Contact** links — Privacy Policy, Terms, and Help & FAQ — are in the footer at the bottom of the page.\n\n"
        "Scrolling you there now! 📬"
    ),
    'landing_section.dashboard': (
        "The **{section}** section is on the landing page. "
        "Click the **Home** icon in the top navigation bar to go there. 🏠"
    ),
    'navigation_login.home': (
        "Opening the **Official Login** dialog for you! 🔑\n\n"
        "You can login as a **Statistical Official** or access the **Admin Portal** "
        "using the form that's about to open."
    ),
    'navigation_login.dashboard': (
        "You're already signed in. 🔐\n\n"
        "To switch accounts, use **Sign Out** at the top-right of the navigation bar, then log in again."
    ),
    'navigation_login.credentials': (
        "I can open the **Official Login** dialog for you right away! 🔑\n\n"
        "However, for your **security**, I won't enter credentials through the chat window — "
        "your username and password should only be typed directly into the secure login form.\n\n"
        "The login dialog is opening now — please type your details there directly. 🛡️"
    ),
    'ui_action_request': (
        "I can switch **Dark / Light mode** and the website language (**English / हिंदी**) for you — "
        "just ask, e.g. *\"turn on dark mode\"* or *\"change language to Hindi\"*.\n\n"
        "For **font size**, use your browser zoom (**Ctrl +** / **Ctrl −**)."
    ),
    'action.theme.dark': "Done! 🌙 I've switched to **Dark Mode** for you.",
    'action.theme.light': "Done! ☀️ I've switched to **Light Mode** for you.",
    'action.theme.toggle': "Done! 🌓 I've toggled the theme for you.",
    'action.language': "Done! I've switched the website to **{language_name}**. 🌐",
    'action.theme_language': "Done! ✅ I've switched to **{theme_name} Mode** and changed the website to **{language_name}**.",
    'theme_name.dark': "Dark",
    'theme_name.light': "Light",
    'language_name.hi': "Hindi",
    'language_name.en': "English",
    'navigation_skill_gap': (
        "**Skill-Gap Centre** 🎯 — in the left sidebar.\n"
        "\n"
        "There you can:\n"
        "• See every competency: your current level vs the level your role needs\n"
        "• Check the evidence behind each level, and use **'Disagree with this level?'** to recheck it\n"
        "• Follow a suggested learning path and this quarter's study plan"
    ),
    'navigation_recommendations': (
        "**Recommendations** ✨ — in the left sidebar.\n"
        "\n"
        "There you'll find AI-ranked courses for your skill gaps, each with the reasons it was matched. Filter by competency to focus on one gap."
    ),
    'navigation_certificates': (
        "**Certificates** 📜 — in the left sidebar.\n"
        "\n"
        "Upload a course certificate there. AI reads it and matches it to your FRAC competencies, and after review it counts as evidence for your levels. You can also track the status of your submissions."
    ),
    'navigation_karma': (
        "**Karma & Rewards** 🏆 — in the left sidebar.\n"
        "\n"
        "There you can see your Karma points, how you earn them (courses, quizzes, daily check-ins) and your points history."
    ),
}
