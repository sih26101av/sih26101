/**
 * FILE: src/pages/LearnerDashboard.tsx
 *
 * The official's home screen at /dashboard/:officialId.
 *
 * Layout: AppShell (navy topbar + section sidebar) wrapping one section at a
 * time. Every section is backed by the single `useLearnerDashboard` fetch — the
 * sidebar only switches which slice of that state is on screen, so navigating
 * never refetches.
 *
 * Sections: dashboard · my-courses · skill-gap · recommendations · assessments
 *           certificates · progress · karma
 */

import React, { useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle, ArrowRight, Award, BarChart3, Bot, Briefcase, BookOpen,
  LayoutDashboard, LifeBuoy, Lock, RefreshCcw, Search, Sparkles,
  Target, TrendingUp, Trophy,
} from "lucide-react";

import { useLearnerDashboard } from "../hooks/useLearnerDashboard";
import { useAuth } from "../context/AuthContext";

import AppShell, { type ShellNavGroup } from "../components/shell/AppShell";
import PageHeader from "../components/shell/PageHeader";
import { usePageTitle } from "../hooks/usePageTitle";
import SectionCard, { SectionAction } from "../components/shell/SectionCard";
import StatCard from "../components/shell/StatCard";

import ProfileHeader from "../components/dashboard/ProfileHeader";
import SkillGapCard from "../components/dashboard/SkillGapCard";
import MyCoursesView from "../components/dashboard/MyCoursesView";
import ProgressView from "../components/dashboard/ProgressView";
import ChatWidget from "../components/dashboard/ChatWidget";
import KarmaRewardsView from "../components/karma/KarmaRewardsView";
import AssessmentUploadZone from "../components/dashboard/AssessmentUploadZone";
import CertificateUploadZone from "../components/dashboard/CertificateUploadZone";
import CompetencyOverviewTable from "../components/dashboard/CompetencyOverviewTable";
import LearningSnapshot from "../components/dashboard/LearningSnapshot";
import RecentActivityList from "../components/dashboard/RecentActivityList";
import RecommendationsPanel from "../components/dashboard/RecommendationsPanel";
import CareerReadinessCard from "../components/dashboard/CareerReadinessCard";
import { AshokaChakra } from "../components/gov/GovUI";

// ─── Sections ─────────────────────────────────────────────────────────────────
export type TabType =
  | "dashboard" | "my-courses" | "skill-gap" | "recommendations"
  | "assessments" | "certificates" | "progress" | "karma";

const SECTION_META: Record<TabType, { title: string; subtitle: string; crumb: string }> = {
  dashboard:       { title: "Dashboard",        subtitle: "Your learning journey towards a stronger statistical ecosystem", crumb: "Dashboard" },
  "my-courses":    { title: "My Courses",       subtitle: "Active enrolments from the iGOT Karmayogi catalogue",            crumb: "My Courses" },
  "skill-gap":     { title: "Skill-Gap Centre", subtitle: "Evidence-weighted competency baselines against your role requirements", crumb: "Skill-Gap Centre" },
  recommendations: { title: "Recommendations",  subtitle: "AI-matched courses that close your active competency gaps",      crumb: "Recommendations" },
  assessments:     { title: "Assessment Studio",subtitle: "Generate assessments from MoSPI training documents and log verified evidence", crumb: "Assessment Studio" },
  certificates:    { title: "Certificates",     subtitle: "Submit external certificates for FRAC competency verification",  crumb: "Certificates" },
  progress:        { title: "Progress Reports", subtitle: "Competency trajectory and your verified achievement record",     crumb: "Progress Reports" },
  karma:           { title: "Karma & Rewards",  subtitle: "Your karma points, level, streak, daily cap and how to earn more",       crumb: "Karma" },
};

// ─── Loading / error ──────────────────────────────────────────────────────────
const LoadingSkeleton: React.FC = () => (
  <div className="space-y-5" aria-busy="true" aria-label="Loading dashboard">
    <div className="skeleton h-36" />
    <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 xl:grid-cols-5">
      {Array.from({ length: 5 }, (_, i) => <div key={i} className="skeleton h-28" />)}
    </div>
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
      <div className="skeleton h-96 lg:col-span-2" />
      <div className="space-y-5">
        <div className="skeleton h-44" />
        <div className="skeleton h-44" />
      </div>
    </div>
  </div>
);

const ErrorState: React.FC<{ message: string; onRetry: () => void }> = ({ message, onRetry }) => (
  <div className="flex min-h-[55vh] animate-fade-up flex-col items-center justify-center gap-4 p-6">
    <div className="flex h-16 w-16 items-center justify-center rounded-full border border-red-100 bg-red-50 shadow-gov dark:border-red-800/50 dark:bg-red-900/20">
      <AlertTriangle size={30} className="text-accent-rose" />
    </div>
    <h2 className="text-xl font-semibold text-gov-ink dark:text-white">Failed to load dashboard</h2>
    <p className="max-w-sm text-center text-sm text-slate-500 dark:text-slate-400">{message}</p>
    <button onClick={onRetry} className="gov-btn-primary">
      <RefreshCcw size={14} /> Retry
    </button>
  </div>
);

// ─── Sidebar help card ────────────────────────────────────────────────────────
const SidebarHelp: React.FC = () => (
  <div className="rounded-xl border border-gov-line bg-gov-paper p-4 dark:border-slate-700/60 dark:bg-slate-800/50">
    <div className="mb-1.5 flex items-center gap-2">
      <LifeBuoy size={16} className="text-gov-blue dark:text-sky-400" aria-hidden="true" />
      <span className="text-[12.5px] font-semibold text-gov-ink dark:text-white">Need help?</span>
    </div>
    <p className="mb-3 text-[11.5px] leading-relaxed text-slate-500 dark:text-slate-400">
      Reach out to the NSO training support desk.
    </p>
    <a
      href="mailto:support-nsota@mospi.gov.in?subject=Skill%20Intelligence%20Platform%20support"
      className="block w-full rounded-lg border border-gov-navy px-3 py-2 text-center text-[12px] font-semibold text-gov-navy transition-colors hover:bg-gov-navy hover:text-white dark:border-slate-500 dark:text-slate-200 dark:hover:bg-white dark:hover:text-gov-ink"
    >
      Contact Support
    </a>
  </div>
);

// ─── Sidebar illustration (palace art + ministry motto) ───────────────────────
// Hidden on short viewports so it never squeezes the nav list.
const SidebarArt: React.FC = () => (
  <div className="pointer-events-none relative mx-3 mb-3 flex-shrink-0 select-none [@media(max-height:780px)]:hidden" aria-hidden="true">
    <img
      src="/sidebar-palace.webp"
      alt=""
      className="h-[170px] w-full object-cover object-[center_62%] opacity-90 dark:opacity-30"
      style={{
        maskImage: "linear-gradient(to bottom, transparent, black 22%, black 70%, transparent)",
        WebkitMaskImage: "linear-gradient(to bottom, transparent, black 22%, black 70%, transparent)",
      }}
    />
    <div className="absolute bottom-3 left-3">
      <p className="text-[15px] font-semibold leading-snug text-gov-ink dark:text-white">
        Data for a<br />Stronger India
      </p>
      <div className="mt-1.5 flex">
        <span className="h-[3px] w-6 rounded-l-full bg-gov-saffron" />
        <span className="h-[3px] w-6 rounded-r-full bg-gov-green" />
      </div>
    </div>
  </div>
);

// ─── Assessment Studio promo (links into the Assessment Studio section) ───────
const StudioPromo: React.FC<{ onOpenStudio: () => void; onOpenQuizPage: () => void }> = ({
  onOpenStudio, onOpenQuizPage,
}) => (
  <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-gov-navy to-gov-blue p-6 text-white shadow-gov-lg">
    <div className="pointer-events-none absolute -right-10 -bottom-12 text-white/10 transition-transform duration-700 group-hover:rotate-45">
      <AshokaChakra size={160} />
    </div>
    <div className="relative flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div className="flex items-start gap-4">
        <span className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border border-white/20 bg-white/10">
          <Bot size={22} className="text-gov-saffron" aria-hidden="true" />
        </span>
        <div>
          <h3 className="mb-1 text-[15.5px] font-semibold">AI Assessment Studio</h3>
          <p className="max-w-lg text-[12.5px] leading-relaxed text-white/70">
            Upload an NSO training document and the RAG engine generates a competency-tagged
            assessment. Passing it writes verified evidence straight into your baseline.
          </p>
        </div>
      </div>
      <div className="flex flex-shrink-0 flex-wrap gap-2.5">
        <button type="button" onClick={onOpenStudio} className="gov-btn-saffron group/btn">
          Open Studio
          <ArrowRight size={15} className="transition-transform group-hover/btn:translate-x-0.5" />
        </button>
        <button
          type="button"
          onClick={onOpenQuizPage}
          className="inline-flex items-center justify-center gap-2 rounded-lg border-[1.5px] border-white/40 px-5 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-white hover:text-gov-ink"
        >
          Take an Assessment
        </button>
      </div>
    </div>
  </div>
);

// ─── Main ─────────────────────────────────────────────────────────────────────
const LearnerDashboard: React.FC<{ officialId?: string }> = ({ officialId }) => {
  const { user: authUser } = useAuth();
  const navigate = useNavigate();

  // Priority: AuthContext user → prop → first real user from mock server
  const userId = authUser?.username ?? officialId ?? "usr_720465595";

  const {
    profile, skillGaps, recommendations, enrollments, achievements, karma,
    isLoading, error, refetch,
  } = useLearnerDashboard(userId);

  const [retryKey, setRetryKey] = useState(0);
  const [activeTab, setActiveTab] = useState<TabType>("dashboard");
  const [courseFilter, setCourseFilter] = useState("");
  const [search, setSearch] = useState("");

  const activeGaps = useMemo(() => skillGaps.filter((g) => g.gap > 0), [skillGaps]);
  const mandatoryGaps = useMemo(() => activeGaps.filter((g) => g.isMandatory), [activeGaps]);
  const totalAssessed = profile?.competencyProfile.userCompetencies.length ?? 0;

  /** Mean of currentLevel/requiredLevel across assessed competencies. */
  const proficiency = useMemo(() => {
    if (skillGaps.length === 0) return 0;
    const sum = skillGaps.reduce(
      (acc, g) => acc + (g.requiredLevel > 0 ? Math.min(1, g.currentLevel / g.requiredLevel) : 1),
      0,
    );
    return Math.round((sum / skillGaps.length) * 100);
  }, [skillGaps]);

  /** Topbar search filters the competency set the Skill-Gap Centre shows. */
  const searchedGaps = useMemo(() => {
    if (!search.trim()) return skillGaps;
    const t = search.trim().toLowerCase();
    return skillGaps.filter(
      (g) => g.competency.skillName.toLowerCase().includes(t) || g.competency.domain.toLowerCase().includes(t),
    );
  }, [skillGaps, search]);

  // "Find courses" from the gap table / SkillGapCard → filtered recommendations
  const recsRef = useRef<HTMLDivElement>(null);
  const handleFindCourses = (skillName: string) => {
    setCourseFilter(skillName);
    setActiveTab("recommendations");
    setTimeout(() => recsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
  };

  const navGroups: ShellNavGroup[] = [
    {
      items: [
        { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
        { id: "my-courses", label: "My Courses", icon: BookOpen, badge: enrollments.length || undefined },
        { id: "skill-gap", label: "Skill-Gap Centre", icon: Target, badge: activeGaps.length || undefined },
        { id: "recommendations", label: "Recommendations", icon: Sparkles },
        { id: "assessments", label: "Assessment Studio", icon: Bot },
        { id: "certificates", label: "Certificates", icon: Award },
        { id: "progress", label: "Progress Reports", icon: TrendingUp },
        { id: "karma", label: "Karma & Rewards", icon: Trophy },
      ],
    },
  ];

  const meta = SECTION_META[activeTab];
  // GIGW: each section is its own "page" to the user, so give it its own title.
  usePageTitle(meta.title, meta.subtitle);

  // ── Error ───────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div key={retryKey}>
        <AppShell
          groups={navGroups}
          activeId={activeTab}
          onNavigate={(id) => setActiveTab(id as TabType)}
          userName={profile?.govId ?? authUser?.username}
          userRole="Official"
        >
          <ErrorState message={error} onRetry={() => setRetryKey((k) => k + 1)} />
        </AppShell>
      </div>
    );
  }

  return (
    <div key={retryKey}>
      <AppShell
        groups={navGroups}
        activeId={activeTab}
        onNavigate={(id) => setActiveTab(id as TabType)}
        userName={profile?.fullName ?? profile?.govId ?? authUser?.username}
        userRole="Official"
        notificationCount={mandatoryGaps.length}
        onNotificationsClick={() => setActiveTab("skill-gap")}
        searchValue={search}
        onSearchChange={(v) => { setSearch(v); if (v) setActiveTab("skill-gap"); }}
        searchPlaceholder="Search your competencies…"
        sidebarArt={<SidebarArt />}
        sidebarFooter={<SidebarHelp />}
      >
        {isLoading || !profile ? (
          <LoadingSkeleton />
        ) : (
          <>
            {/* The overview banner carries its own date chip, so skip the page header there */}
            {activeTab !== "dashboard" && (
              <PageHeader
                title={meta.title}
                subtitle={meta.subtitle}
                breadcrumb={["Home", "Learner", meta.crumb]}
                dateCaption="Keep learning, keep growing!"
              />
            )}

            {/* ── Overview ──────────────────────────────────────────────── */}
            {activeTab === "dashboard" && (
              <div className="animate-fade-up space-y-5">
                <ProfileHeader profile={profile} totalAssessed={totalAssessed} />

                <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 xl:grid-cols-5 [&>*:last-child]:col-span-2 md:[&>*:last-child]:col-span-1">
                  <StatCard index={0} icon={Briefcase} tone="blue" label="Competencies Assessed" value={totalAssessed} />
                  <StatCard index={1} icon={AlertTriangle} tone="rose" label="Active Gaps" value={activeGaps.length} onClick={() => setActiveTab("skill-gap")} />
                  <StatCard index={2} icon={Lock} tone="orange" label="Mandatory Gaps" value={mandatoryGaps.length} onClick={() => setActiveTab("skill-gap")} />
                  <StatCard index={3} icon={Search} tone="green" label="Recommendations" value={recommendations.length} onClick={() => setActiveTab("recommendations")} />
                  <StatCard index={4} icon={BarChart3} tone="purple" label="Overall Proficiency" value={`${proficiency}%`} progress={proficiency} />
                </div>

                <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-3">
                  <div className="space-y-5 xl:col-span-2">
                    <CompetencyOverviewTable
                      skillGaps={skillGaps}
                      onFindCourses={handleFindCourses}
                      onViewDetailed={() => setActiveTab("skill-gap")}
                    />

                    {/* Sits under the table so the left column fills the height of the right one */}
                    <SectionCard
                      title="Recent Activity"
                      action={<SectionAction label="View all" onClick={() => setActiveTab("progress")} />}
                    >
                      <RecentActivityList achievements={achievements} />
                    </SectionCard>
                  </div>

                  <div className="space-y-5">
                    <SectionCard
                      title="Your Learning Snapshot"
                      action={<SectionAction label="My Courses" onClick={() => setActiveTab("my-courses")} />}
                    >
                      <LearningSnapshot enrollments={enrollments} />
                    </SectionCard>
                    <CareerReadinessCard
                      userId={userId}
                      refreshKey={skillGaps.map(g => `${g.competency.compId}:${g.currentLevel}`).join("|")}
                    />
                  </div>
                </div>

                <SectionCard
                  title="Recommended for You"
                  subtitle="AI-matched against your active competency gaps"
                  action={<SectionAction label="View all" onClick={() => setActiveTab("recommendations")} />}
                >
                  <RecommendationsPanel
                    recommendations={recommendations}
                    filter=""
                    onClearFilter={() => setCourseFilter("")}
                    limit={3}
                  />
                </SectionCard>
              </div>
            )}

            {/* ── My Courses ────────────────────────────────────────────── */}
            {activeTab === "my-courses" && (
              <div className="animate-fade-up">
                <MyCoursesView enrollments={enrollments} />
              </div>
            )}

            {/* ── Skill-Gap Centre ──────────────────────────────────────── */}
            {activeTab === "skill-gap" && (
              <div className="animate-fade-up space-y-5">
                <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
                  <StatCard index={0} icon={Briefcase} tone="blue" label="Competencies Assessed" value={totalAssessed} />
                  <StatCard index={1} icon={AlertTriangle} tone="rose" label="Active Gaps" value={activeGaps.length} />
                  <StatCard index={2} icon={Lock} tone="orange" label="Mandatory Gaps" value={mandatoryGaps.length} />
                  <StatCard index={3} icon={BarChart3} tone="purple" label="Overall Proficiency" value={`${proficiency}%`} progress={proficiency} />
                </div>

                {search.trim() && (
                  <p className="text-[12.5px] text-slate-500 dark:text-slate-400">
                    Showing {searchedGaps.length} of {skillGaps.length} competencies matching “{search}”.{" "}
                    <button type="button" onClick={() => setSearch("")} className="font-semibold text-gov-blue hover:underline dark:text-sky-400">
                      Clear
                    </button>
                  </p>
                )}

                <SkillGapCard skillGaps={searchedGaps} onFindCourses={handleFindCourses} officialId={userId} onLevelChanged={refetch} />
              </div>
            )}

            {/* ── Recommendations ───────────────────────────────────────── */}
            {activeTab === "recommendations" && (
              <div ref={recsRef} className="animate-fade-up">
                <SectionCard
                  title="Recommended Learning Pathway"
                  subtitle="Hybrid FAISS + BM25 retrieval, re-ranked against your evidence-weighted gaps"
                  action={
                    <span className="chip bg-gov-navy text-white dark:bg-sky-700">
                      {recommendations.length} course{recommendations.length === 1 ? "" : "s"}
                    </span>
                  }
                >
                  <RecommendationsPanel
                    recommendations={recommendations}
                    filter={courseFilter}
                    onClearFilter={() => setCourseFilter("")}
                    gridClassName="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4"
                  />
                </SectionCard>
              </div>
            )}

            {/* ── Assessment Studio ─────────────────────────────────────── */}
            {activeTab === "assessments" && (
              <div className="animate-fade-up space-y-5">
                <StudioPromo
                  onOpenStudio={() => navigate("/assessment")}
                  onOpenQuizPage={() => navigate("/assessment")}
                />

                <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-3">
                  <div className="xl:col-span-2">
                    <SectionCard
                      title="Generate an Assessment"
                      subtitle="Upload a training document — questions are generated and graded against FRAC competencies"
                    >
                      <AssessmentUploadZone
                        userId={userId}
                        onQuizPassed={refetch}
                        onViewProgress={() => setActiveTab("progress")}
                      />
                    </SectionCard>
                  </div>

                  <SectionCard
                    title="Skill-Gap Centre"
                    subtitle="The gaps your next assessment should target"
                    action={<SectionAction label="Open" onClick={() => setActiveTab("skill-gap")} />}
                  >
                    <ul className="space-y-2.5">
                      {activeGaps
                        .slice()
                        .sort((a, b) => b.gap - a.gap)
                        .slice(0, 5)
                        .map((g) => (
                          <li key={g.competency.compId} className="flex items-center gap-3">
                            <span className="min-w-0 flex-1">
                              <span className="block truncate text-[12.5px] font-semibold text-gov-ink dark:text-white">
                                {g.competency.skillName}
                              </span>
                              <span className="text-[11px] text-slate-400">{g.competency.domain}</span>
                            </span>
                            <span className="chip bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300">
                              gap {g.gap}
                            </span>
                          </li>
                        ))}
                      {activeGaps.length === 0 && (
                        <li className="py-6 text-center text-[13px] text-slate-400">
                          No active gaps — every role requirement is currently met.
                        </li>
                      )}
                    </ul>
                  </SectionCard>
                </div>
              </div>
            )}

            {/* ── Certificates ──────────────────────────────────────────── */}
            {activeTab === "certificates" && (
              <div className="animate-fade-up grid grid-cols-1 items-start gap-5 xl:grid-cols-2">
                <SectionCard title="Upload a Certificate" subtitle="Extracted skills are matched to FRAC competencies and logged as documented evidence">
                  <CertificateUploadZone onUploaded={refetch} />
                </SectionCard>
                <SectionCard title="Verified Achievements" subtitle="Quiz passes and accepted certificates on your record">
                  <RecentActivityList achievements={achievements} limit={8} />
                </SectionCard>
              </div>
            )}

            {/* ── Progress Reports ──────────────────────────────────────── */}
            {activeTab === "progress" && (
              <div className="animate-fade-up space-y-5">
                <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-3">
                  <div className="xl:col-span-2">
                    <ProgressView achievements={achievements} skillGaps={skillGaps} />
                  </div>
                  <SectionCard title="Your Learning Snapshot">
                    <LearningSnapshot enrollments={enrollments} />
                  </SectionCard>
                </div>
              </div>
            )}

            {/* ── Karma ─────────────────────────────────────────────────── */}
            {activeTab === "karma" && (
              <div className="animate-fade-up">
                <KarmaRewardsView karma={karma} userId={userId} />
              </div>
            )}
          </>
        )}
      </AppShell>

      {/* ── Gyan AI Chat Widget ─────────────────────────────────────────── */}
      {profile && (
        <ChatWidget
          officialId={userId}
          fullName={profile.fullName}
          govId={profile.govId}
          jobRole={profile.jobRole.title}
          department={profile.department}
          skillGaps={skillGaps}
          recommendations={recommendations}
          onNavigate={(action) => {
            if (action.type === "tab") {
              // Legacy targets plus the sections introduced by the sidebar.
              const tabMap: Record<string, TabType> = {
                dashboard: "dashboard",
                "my-courses": "my-courses",
                progress: "progress",
                "skill-gap": "skill-gap",
                "skill-gaps": "skill-gap",
                recommendations: "recommendations",
                courses: "recommendations",
                assessments: "assessments",
                assessment: "assessments",
                certificates: "certificates",
                karma: "karma",
              };
              const target = tabMap[action.target];
              if (target) setActiveTab(target);
            } else if (action.type === "redirect") {
              navigate(action.target);
            }
          }}
        />
      )}
    </div>
  );
};

export default LearnerDashboard;
