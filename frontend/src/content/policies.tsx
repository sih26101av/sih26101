/**
 * FILE: src/content/policies.tsx
 *
 * The statutory pages GIGW 3.0 requires a Government of India website to
 * publish, and to link from the footer of every page. They are held here as
 * data so `pages/PolicyPage.tsx` can render all of them from one route, and so
 * the footer, the sitemap and the accessibility bar all reference one list.
 *
 * Wording follows the standard Government of India policy text, adapted to this
 * portal (MoSPI / NSO training). Officer names and phone numbers are left as
 * roles rather than invented individuals — fill them in before a real launch.
 */

export interface PolicyBlock {
  /** Sub-heading above the block. */
  heading?: string;
  /** Body paragraphs. */
  p?: string[];
  /** Bulleted points. */
  ul?: string[];
  /** A simple table: the first row is the header row. */
  table?: { caption?: string; rows: string[][] };
  /** Internal route links (used by the sitemap page). */
  links?: { label: string; to: string; note?: string }[];
}

export interface Policy {
  slug: string;
  title: string;
  /** Shown under the English title on the page masthead. */
  titleHi: string;
  /** One-line strapline under the page title, also used as the meta description. */
  summary: string;
  blocks: PolicyBlock[];
}

/** Footer / sitemap ordering. Terms first — that is the GIGW convention. */
export const POLICY_LINKS: { slug: string; title: string }[] = [
  { slug: 'terms-and-conditions', title: 'Terms & Conditions' },
  { slug: 'privacy-policy', title: 'Privacy Policy' },
  { slug: 'copyright-policy', title: 'Copyright Policy' },
  { slug: 'hyperlinking-policy', title: 'Hyperlinking Policy' },
  { slug: 'disclaimer', title: 'Disclaimer' },
  { slug: 'accessibility-statement', title: 'Accessibility Statement' },
  { slug: 'screen-reader-access', title: 'Screen Reader Access' },
  { slug: 'help', title: 'Help' },
  { slug: 'feedback', title: 'Feedback & Contact' },
  { slug: 'sitemap', title: 'Sitemap' },
];

const POLICY_LIST: Policy[] = [
  // ── Terms & Conditions ────────────────────────────────────────────────────
  {
    slug: 'terms-and-conditions',
    title: 'Terms & Conditions',
    titleHi: 'नियम एवं शर्तें',
    summary: 'The conditions on which officials of the National Statistical System may use this portal.',
    blocks: [
      {
        p: [
          'This website is owned and operated by the Ministry of Statistics and Programme Implementation (MoSPI), Government of India. By accessing the portal you accept the terms set out below. If you do not accept them, please do not use the portal.',
          'Access is restricted to serving officials of the National Statistical System and to administrators authorised by the Training Division. Credentials are issued against an iGOT Karmayogi user identity and are personal to the officer they are issued to.',
        ],
      },
      {
        heading: 'Use of the portal',
        ul: [
          'You are responsible for every action taken under your credentials. Do not share your password, and change it immediately if you believe it has been disclosed.',
          'Assessments must be attempted by the officer whose account is used. Competency levels recorded by this portal are written back to the national registry and are relied on for career and training decisions.',
          'Documents, recordings and links you upload for assessment generation must be material you are authorised to use. Do not upload classified material, personal data of third parties, or anything covered by the Official Secrets Act, 1923.',
          'Do not attempt to probe, scan or test the vulnerability of the portal, or to breach its authentication or access controls.',
        ],
      },
      {
        heading: 'Accuracy of content',
        p: [
          'Competency baselines, skill gaps and course recommendations on this portal are produced by automated analysis of the evidence recorded against your profile. They are decision-support outputs, not determinations. Where an output conflicts with an official record such as APAR, ACBP or the iGOT Karmayogi registry, the official record prevails.',
          'MoSPI makes no warranty that the portal will be uninterrupted or error-free, and reserves the right to modify or withdraw any part of it without notice.',
        ],
      },
      {
        heading: 'Governing law',
        p: [
          'These terms are governed by the laws of India. Any dispute arising under them is subject to the exclusive jurisdiction of the courts at New Delhi.',
        ],
      },
    ],
  },

  // ── Privacy Policy ────────────────────────────────────────────────────────
  {
    slug: 'privacy-policy',
    title: 'Privacy Policy',
    titleHi: 'गोपनीयता नीति',
    summary: 'What this portal records about you, why it records it, and how it is used.',
    blocks: [
      {
        p: [
          'This portal does not collect personal information from you for any purpose other than delivering competency analysis and training recommendations to you and to the authorities responsible for your capacity building.',
        ],
      },
      {
        heading: 'Information we hold',
        ul: [
          'Identity and service details drawn from the iGOT Karmayogi registry: your user identity, name, designation, office, cadre and role mapping. The portal reads these; it does not create them.',
          'Learning evidence you generate here: assessment attempts and scores, uploaded certificates and the competency claims extracted from them, course enrolments and completions, karma points, and assistant conversations used to resolve your query.',
          'Technical information needed to run the service: the session cookie that keeps you signed in, and server logs of requests, retained only as long as needed for security and audit.',
        ],
      },
      {
        heading: 'How the information is used',
        p: [
          'Your evidence is used to compute your competency baseline, identify skill gaps against the Framework of Roles, Activities and Competencies (FRAC) for your role, and recommend iGOT Karmayogi courses. Where you pass an assessment, the resulting competency level is written back to the iGOT Karmayogi registry.',
          'Administrators of your ministry see aggregated workforce views. Individual assessment content is visible to you, and to officers authorised to review certificate submissions.',
          'We do not sell, trade or rent your information to anyone. It is not disclosed to any third party outside the Government of India except where required by law.',
        ],
      },
      {
        heading: 'Cookies and local storage',
        p: [
          'The portal sets one essential cookie: an HTTP-only refresh-token cookie that keeps your session alive and is cleared when you sign out. Your accessibility preferences — text size, contrast and language — are stored in your browser and never leave your device. No advertising or third-party tracking cookie is set.',
        ],
      },
      {
        heading: 'Your rights',
        p: [
          'You may ask to see the evidence recorded against your profile and to have an inaccurate record corrected. Raise such a request through your division training nodal officer or the Web Information Manager named in the footer of this page.',
        ],
      },
    ],
  },

  // ── Copyright Policy ──────────────────────────────────────────────────────
  {
    slug: 'copyright-policy',
    title: 'Copyright Policy',
    titleHi: 'कॉपीराइट नीति',
    summary: 'Terms on which material published on this portal may be reproduced.',
    blocks: [
      {
        p: [
          'Material featured on this portal may be reproduced free of charge in any format or medium, provided it is reproduced accurately and not used in a derogatory manner or in a misleading context. Where the material is being published or issued to others, the source must be prominently acknowledged.',
          'Permission to reproduce this material does not extend to any material on this portal identified as the copyright of a third party. Authorisation to reproduce such material must be obtained from the copyright holder concerned.',
          'Course content, assessments and competency frameworks surfaced through this portal originate from the iGOT Karmayogi platform and from the Framework of Roles, Activities and Competencies (FRAC) maintained by the Capacity Building Commission, and remain the property of their respective owners.',
        ],
      },
      {
        heading: 'National emblem',
        p: [
          'The State Emblem of India is used on this portal in accordance with the State Emblem of India (Prohibition of Improper Use) Act, 2005. It may not be reproduced from these pages for any other purpose.',
        ],
      },
    ],
  },

  // ── Hyperlinking Policy ───────────────────────────────────────────────────
  {
    slug: 'hyperlinking-policy',
    title: 'Hyperlinking Policy',
    titleHi: 'हाइपरलिंकिंग नीति',
    summary: 'How this portal links out, and how others may link to it.',
    blocks: [
      {
        heading: 'Links to external websites',
        p: [
          'At several places on this portal you will find links to other websites and portals. These links have been placed for your convenience. MoSPI is not responsible for the contents of any linked site, and the presence of a link does not imply endorsement of the views expressed there. We cannot guarantee that such links will work all of the time and have no control over the availability of the linked pages.',
          'Links that leave this portal are marked with an external-link icon and open in a new window, so you can tell before you follow them.',
        ],
      },
      {
        heading: 'Links to this portal by other websites',
        p: [
          'We do not object to you linking directly to the information hosted on this portal, and no prior permission is required. However, we would like you to inform us about any link provided to this portal so that you can be informed of any change or update.',
          'We do not permit our pages to be loaded into frames on your site. The pages belonging to this portal must load into a newly opened browser window of the user.',
        ],
      },
    ],
  },

  // ── Disclaimer ────────────────────────────────────────────────────────────
  {
    slug: 'disclaimer',
    title: 'Disclaimer',
    titleHi: 'अस्वीकरण',
    summary: 'The standing of the information published on this portal.',
    blocks: [
      {
        p: [
          'This portal is a capacity-building prototype developed for the Ministry of Statistics and Programme Implementation. Information is provided on an "as is" basis with no warranty of completeness, accuracy, timeliness, or of the results obtained from its use.',
          'Competency baselines, skill gaps, recommended courses, quiz items and assistant responses on this portal are generated by automated models from the evidence available to them. They support a decision; they do not replace one. Nothing here should be treated as a legal statement of an officer qualifications, nor as a substitute for the official records held in iGOT Karmayogi, HRMS or APAR.',
          'Course catalogue and role data shown during evaluation is served from a mock iGOT Karmayogi environment maintained for demonstration, and is not live national data.',
          'In no event will MoSPI be liable for any loss or damage including, without limitation, indirect or consequential loss, arising out of or in connection with the use of this portal.',
          'These terms are governed by and construed in accordance with the laws of India. Any dispute arising under them is subject to the exclusive jurisdiction of the courts of India.',
        ],
      },
    ],
  },

  // ── Accessibility Statement ───────────────────────────────────────────────
  {
    slug: 'accessibility-statement',
    title: 'Accessibility Statement',
    titleHi: 'सुगम्यता विवरण',
    summary: 'This portal is built to WCAG 2.1 level AA and to GIGW 3.0 — what that means in practice, and where we fall short.',
    blocks: [
      {
        p: [
          'We are committed to ensuring that this portal is accessible to all users irrespective of device, technology or ability. It is built to comply with the Guidelines for Indian Government Websites (GIGW 3.0) and with the Web Content Accessibility Guidelines (WCAG) 2.1 at level AA, as required by the Rights of Persons with Disabilities Act, 2016.',
        ],
      },
      {
        heading: 'Accessibility features',
        ul: [
          'Text size — the A− / A / A+ control in the strip at the top of every page resizes the whole interface. Your choice is remembered on this device.',
          'High contrast — the contrast control in the same strip switches the portal to a black background with high-contrast text and yellow links, for users with low vision.',
          'Dark and light themes, with the operating-system preference honoured on first visit.',
          'Screen reader access — a read-aloud control on the public pages, plus a semantic page structure (landmarks, headings in order, labelled form fields, tables with header cells) that works with the screen readers listed on the Screen Reader Access page.',
          'Keyboard access — every control can be reached and operated with the keyboard alone. A visible focus outline follows the keyboard, and "Skip to main content" is the first stop on every page.',
          'Reduced motion — animation is suppressed when your operating system asks for reduced motion.',
          'Bilingual interface — English and हिन्दी, with the page language exposed to assistive technology.',
          'Printable pages — navigation, widgets and decoration are dropped when a page is printed.',
        ],
      },
      {
        heading: 'Conformance and known limitations',
        p: [
          'We assess this portal against WCAG 2.1 AA using keyboard-only navigation, screen reader testing and automated checks. We believe it substantially conforms. The following are known gaps we are working on:',
        ],
        ul: [
          'Some data visualisations (donuts, trend charts) convey information graphically. Each is accompanied by the same figures in a table or a text summary, but the charts themselves are not independently navigable.',
          'Documents you upload for assessment generation — PDFs, presentations and recordings — are your own material and their accessibility is outside our control.',
          'Content reached through links to iGOT Karmayogi and other national portals is governed by those portals own accessibility statements.',
        ],
      },
      {
        heading: 'Tell us about a barrier',
        p: [
          'If you cannot access any content or use any feature of this portal, please write to the Web Information Manager named in the footer, or use the feedback page. Describe the page, what you were trying to do and the assistive technology you were using. We will respond and, where the fix is not immediate, offer the information in a form you can use.',
        ],
      },
    ],
  },

  // ── Screen Reader Access ──────────────────────────────────────────────────
  {
    slug: 'screen-reader-access',
    title: 'Screen Reader Access',
    titleHi: 'स्क्रीन रीडर एक्सेस',
    summary: 'The portal is tested with the screen readers listed below, and carries a built-in read-aloud control.',
    blocks: [
      {
        p: [
          'This portal complies with the World Wide Web Consortium (W3C) Web Content Accessibility Guidelines 2.1 level AA. It can be read with a screen reader, and the public pages also carry a built-in "Listen to this page" control in the strip at the top. That control reads the main content aloud in the language the page is set to, using your browser own speech engine — nothing is sent to an external service.',
        ],
      },
      {
        heading: 'Screen readers you can use',
        table: {
          caption: 'Screen reader software and where to obtain it',
          rows: [
            ['Screen reader', 'Website', 'Free or commercial'],
            ['NVDA', 'nvaccess.org', 'Free'],
            ['Orca (Linux)', 'help.gnome.org/users/orca', 'Free'],
            ['Narrator (Windows)', 'Built into Windows', 'Free'],
            ['VoiceOver (macOS and iOS)', 'Built into Apple devices', 'Free'],
            ['TalkBack (Android)', 'Built into Android', 'Free'],
            ['JAWS', 'freedomscientific.com', 'Commercial'],
            ['Window-Eyes', 'gwmicro.com', 'Commercial'],
          ],
        },
      },
      {
        heading: 'Keyboard navigation',
        ul: [
          'Tab and Shift+Tab move forward and backward through the interactive controls on a page.',
          'The first Tab on any page lands on "Skip to main content" — press Enter to jump past the navigation.',
          'Enter or Space activate the focused button, link or menu item.',
          'Escape closes the navigation drawer, the account menu, the search row and any open dialog.',
          'Arrow keys move within menus and the assistant suggestion list.',
        ],
      },
    ],
  },

  // ── Help ──────────────────────────────────────────────────────────────────
  {
    slug: 'help',
    title: 'Help',
    titleHi: 'सहायता',
    summary: 'How to sign in, read your skill gaps, take an assessment and get your competency level updated.',
    blocks: [
      {
        heading: 'Signing in',
        p: [
          'Use the iGOT Karmayogi user identity issued to you (it looks like usr_XXXXXXXXX) and the password supplied by your training nodal officer. You will be asked to change that password the first time you sign in. Choose "Official Login" for a learner account and "Admin Portal" for an administrator account — both use the same form.',
        ],
      },
      {
        heading: 'Reading your dashboard',
        ul: [
          'Skill Gap Centre — each competency shows your current level, the level your role requires, the size of the gap and how confident the system is in that reading. The evidence bars beneath show which channels (knowledge, application, usage, supervisor) the reading is based on.',
          'Recommendations — iGOT Karmayogi courses matched to your open gaps, with mandatory ACBP courses marked. The study plan is sized to your quarterly training budget.',
          'Assessment Studio — upload a document, a recording or a video link and the portal generates a quiz from it, with every answer traceable to a passage in your material.',
          'Certificates — upload a certificate you earned elsewhere and the portal extracts the competency claim for review.',
          'Karma — points earned for completing courses, passing assessments and keeping a learning streak.',
        ],
      },
      {
        heading: 'Getting a competency level updated',
        p: [
          'Score 70% or more on an assessment for a competency and the portal records the evidence and writes the improved level back to the iGOT Karmayogi registry. A certificate you upload is reviewed by an administrator before it counts.',
        ],
      },
      {
        heading: 'Asking Gyan',
        p: [
          'Gyan is the in-portal assistant, available from the button in the bottom-right corner of every page. Ask it about your gaps, your courses or how a part of the portal works, in English or Hindi. It answers from the data already loaded for your account.',
        ],
      },
      {
        heading: 'If something does not work',
        p: [
          'Report it to your division training nodal officer, or use the feedback page. Include the page you were on, what you expected and what happened.',
        ],
      },
    ],
  },

  // ── Feedback & Contact ────────────────────────────────────────────────────
  {
    slug: 'feedback',
    title: 'Feedback & Contact',
    titleHi: 'प्रतिक्रिया एवं संपर्क',
    summary: 'Who to write to about this portal, its content and its accessibility.',
    blocks: [
      {
        p: [
          'Your suggestions about the design, content and accessibility of this portal are welcome and help us improve it. Please route feedback through the channel that fits your query.',
        ],
      },
      {
        heading: 'Web Information Manager',
        p: [
          'Director (Training Division), National Statistical Office.',
          'Ministry of Statistics and Programme Implementation, Sardar Patel Bhavan, Sansad Marg, New Delhi − 110001.',
          'For content, accessibility and technical queries about this portal.',
        ],
      },
      {
        heading: 'Training nodal officer',
        p: [
          'For queries about your own account, your competency record, an assessment result or a certificate under review, contact the training nodal officer of your division in the first instance. They can escalate to the Training Division where needed.',
        ],
      },
      {
        heading: 'iGOT Karmayogi',
        p: [
          'For queries about a course, its content or its certificate, write to the iGOT Karmayogi support desk — this portal surfaces that catalogue but does not author it.',
        ],
      },
      {
        heading: 'Reporting an accessibility barrier',
        p: [
          'Tell us the page, what you were trying to do, and the assistive technology and browser you were using. We aim to acknowledge accessibility reports and to provide the information in an alternative accessible form while a fix is prepared.',
        ],
      },
    ],
  },

  // ── Sitemap ───────────────────────────────────────────────────────────────
  {
    slug: 'sitemap',
    title: 'Sitemap',
    titleHi: 'साइट मानचित्र',
    summary: 'Every section of this portal on one page.',
    blocks: [
      {
        heading: 'Public pages',
        links: [
          { label: 'Home', to: '/', note: 'About the platform, its capabilities and how to sign in' },
          { label: 'Official Login', to: '/login', note: 'Sign in with your iGOT Karmayogi identity' },
        ],
      },
      {
        heading: 'For officials (sign-in required)',
        links: [
          { label: 'Dashboard', to: '/dashboard-redirect', note: 'Overview: competencies, snapshot, activity and readiness' },
          { label: 'My Courses', to: '/dashboard-redirect', note: 'Your iGOT Karmayogi enrolments and their progress' },
          { label: 'Skill Gap Centre', to: '/dashboard-redirect', note: 'Gap per competency, the evidence behind it and the study order' },
          { label: 'Recommendations', to: '/dashboard-redirect', note: 'Courses matched to your open gaps' },
          { label: 'Assessment Studio', to: '/assessment', note: 'Generate a quiz from a document, recording or video' },
          { label: 'Certificates', to: '/dashboard-redirect', note: 'Submit a certificate for competency credit' },
          { label: 'Progress', to: '/dashboard-redirect', note: 'Your learning trend over time' },
          { label: 'Karma & Rewards', to: '/dashboard-redirect', note: 'Points, streak and badges' },
          { label: 'Change Password', to: '/change-password' },
        ],
      },
      {
        heading: 'For administrators (sign-in required)',
        links: [
          { label: 'Admin Dashboard', to: '/admin', note: 'Ministry-wide capacity, trends and workforce insights' },
          { label: 'Certificate Review Queue', to: '/admin', note: 'Approve or reject submitted certificates' },
          { label: 'System Health', to: '/admin', note: 'Backend, mock iGOT server and AI service status' },
        ],
      },
      {
        heading: 'Website policies',
        links: POLICY_LINKS.filter((p) => p.slug !== 'sitemap').map((p) => ({ label: p.title, to: `/policy/${p.slug}` })),
      },
    ],
  },
];

export const POLICIES: Record<string, Policy> = Object.fromEntries(
  POLICY_LIST.map((policy) => [policy.slug, policy])
);

export function getPolicy(slug?: string): Policy | undefined {
  return slug ? POLICIES[slug] : undefined;
}
