/**
 * FILE: src/components/dashboard/ProfileHeader.tsx
 *
 * Overview hero: avatar + identity on the left, date chip and ministry strapline
 * on the right, over `public/profile-banner.webp` (waves, dotted India map,
 * growth bars, chakra). In dark mode the art is dimmed under a navy scrim.
 */

import React from "react";
import { BadgeCheck, Building2, CalendarDays, Clock, User } from "lucide-react";
import type { Official } from "../../types/domain";

interface ProfileHeaderProps {
  profile: Official;
  totalAssessed: number;
}

const formatDate = (iso: string): string => {
  try {
    return new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
  } catch { return "N/A"; }
};

const TAGLINE = ["Learn", "Analyse", "Contribute", "Grow"];

const ProfileHeader: React.FC<ProfileHeaderProps> = ({ profile, totalAssessed }) => {
  const displayName = profile.fullName && profile.fullName !== "MoSPI Official" ? profile.fullName : profile.govId;
  const initials = displayName.substring(0, 1).toUpperCase();
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long", day: "numeric", month: "short", year: "numeric",
  });

  const chip =
    "flex items-center gap-1.5 rounded-full border border-gov-line bg-white/85 px-3 py-1.5 text-gov-ink shadow-sm backdrop-blur-sm " +
    "dark:border-white/10 dark:bg-white/10 dark:text-white";

  return (
    <div className="relative overflow-hidden rounded-2xl border border-gov-line bg-gradient-to-r from-white via-[#f3f8fe] to-[#e6f1fc] shadow-gov dark:border-slate-700/60 dark:bg-gov-ink">
      {/* Banner art — fitted to the banner height and pinned right so the map, bars and
          chakra are never cropped; the left edge fades into the base colour. */}
      <div
        className="pointer-events-none absolute inset-y-0 right-0 hidden aspect-[3/1] bg-no-repeat dark:opacity-25 sm:block"
        style={{
          backgroundImage: "url('/profile-banner.webp')",
          backgroundSize: "100% 100%",
          maskImage: "linear-gradient(90deg, transparent, black 30%)",
          WebkitMaskImage: "linear-gradient(90deg, transparent, black 30%)",
        }}
        aria-hidden="true"
      />
      {/* Keeps the identity block legible on narrow screens where the art slides under it */}
      <div
        className="pointer-events-none absolute inset-0 bg-gradient-to-r from-white/70 via-white/20 to-transparent dark:from-gov-ink/90 dark:via-gov-ink/60 dark:to-gov-ink/30"
        aria-hidden="true"
      />

      <div className="relative z-10 flex flex-col gap-4 px-4 pb-6 pt-5 sm:gap-6 sm:px-6 sm:py-7 md:px-8 xl:flex-row xl:items-center xl:justify-between">
        {/* Left: Avatar + Info */}
        <div className="flex min-w-0 items-start gap-3.5 sm:items-center sm:gap-5 md:gap-6">
          <div className="relative h-[64px] w-[64px] flex-shrink-0 sm:h-[92px] sm:w-[92px] rounded-full bg-[conic-gradient(#ff9933_0_33%,#e8eef7_33%_66%,#138808_66%_100%)] p-[4px] shadow-gov-lg">
            <div className="flex h-full w-full items-center justify-center rounded-full border-[3px] border-white bg-gov-navy dark:border-gov-ink">
              <span className="text-[24px] font-bold text-white sm:text-[34px]">{initials}</span>
            </div>
            <span className="absolute bottom-0 right-0 flex h-5 w-5 items-center sm:bottom-1 sm:right-1 sm:h-6 sm:w-6 justify-center rounded-full border-2 border-white bg-gov-green dark:border-gov-ink">
              <BadgeCheck size={13} className="text-white" />
            </span>
          </div>

          <div className="min-w-0">
            <div className="mb-0.5 text-[13px] font-medium sm:text-[15px] text-gov-ink/80 dark:text-white/80">Welcome back,</div>
            <div className="mb-1 flex flex-wrap items-center gap-x-3 gap-y-1">
              <h1 className="break-words text-[21px] font-bold sm:text-[26px] leading-tight tracking-tight text-gov-ink dark:text-white md:text-[30px]">
                {displayName}
              </h1>
              <span className="flex items-center gap-1 rounded-full border border-gov-green/40 bg-green-50 px-2 py-0.5 text-[9.5px] font-bold uppercase tracking-wider text-gov-green dark:bg-gov-green/25 dark:text-[#86efac]">
                <BadgeCheck size={11} />
                Verified Official
              </span>
            </div>
            <p className="mb-3 text-[14px] font-medium text-gov-navy sm:text-[16px] dark:text-white/80">{profile.jobRole.title}</p>
            <div className="-ml-[78px] flex flex-wrap items-center gap-2 text-[11px] font-medium sm:ml-0 sm:text-[11.5px]">
              <span className={chip}>
                <User size={13} className="text-gov-saffron" /> {profile.govId}
              </span>
              <span className={chip}>
                <Building2 size={13} className="text-gov-saffron" /> {profile.department}
              </span>
              <span className={chip}>
                <Clock size={13} className="text-gov-saffron" /> Last assessed: {formatDate(profile.competencyProfile.lastEvaluatedDate)}
              </span>
            </div>
          </div>
        </div>

        {/* Right: date chip + ministry strapline (sits left of the map/bars art) */}
        <div className="flex flex-col items-start gap-3 border-t border-gov-line/70 pt-4 dark:border-white/10 sm:gap-4 sm:border-0 sm:pt-0 xl:mr-[330px] xl:items-center xl:text-center">
          <div className="hidden items-center gap-2.5 sm:flex rounded-xl border border-gov-line bg-white/90 px-3.5 py-2 shadow-sm backdrop-blur-sm dark:border-white/10 dark:bg-white/10">
            <CalendarDays size={18} className="text-gov-navy dark:text-sky-300" aria-hidden="true" />
            <span className="leading-tight">
              <span className="block text-[12px] font-semibold text-gov-ink dark:text-white">{today}</span>
              <span className="block text-[10.5px] text-slate-500 dark:text-slate-300">Keep learning, keep growing!</span>
            </span>
          </div>
          <p className="text-[14px] font-medium italic leading-snug sm:text-[15px] text-gov-navy dark:text-white/90 md:text-[16px]">
            “Data for a Stronger India<br className="hidden sm:block" /> Through a More Competent Workforce”
          </p>
          <span className="text-[11px] text-slate-500 dark:text-white/60">
            <span className="font-bold text-gov-ink dark:text-white">{totalAssessed}</span> competencies assessed
          </span>
        </div>
      </div>

      {/* Motto, far right under the chakra */}
      <ul className="absolute bottom-6 right-5 z-10 hidden space-y-0.5 text-right text-[9px] font-semibold uppercase tracking-[0.18em] text-gov-navy/60 dark:text-white/50 xl:block">
        {TAGLINE.map((w) => <li key={w}>{w}</li>)}
      </ul>

      {/* Saffron / green accent at the bottom edge */}
      <div className="absolute bottom-0 left-1/2 z-10 flex -translate-x-1/2" aria-hidden="true">
        <span className="h-[3px] w-14 bg-gov-saffron" />
        <span className="h-[3px] w-14 bg-gov-green" />
      </div>
    </div>
  );
};

export default ProfileHeader;
