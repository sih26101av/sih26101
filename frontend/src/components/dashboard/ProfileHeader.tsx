/**
 * FILE: src/components/dashboard/ProfileHeader.tsx
 */

import React from "react";
import { BadgeCheck, Building2, Clock, User } from "lucide-react";
import type { Official } from "../../types/domain";
import { AshokaChakra, CountUp } from "../gov/GovUI";

interface ProfileHeaderProps {
  profile: Official;
  totalAssessed: number;
}

const formatDate = (iso: string): string => {
  try {
    return new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
  } catch { return "N/A"; }
};

const ProfileHeader: React.FC<ProfileHeaderProps> = ({ profile, totalAssessed }) => {
  const displayName = profile.fullName && profile.fullName !== "MoSPI Official" ? profile.fullName : profile.govId;
  const initials = displayName.substring(0, 1).toUpperCase();

  return (
    <div className="relative rounded-2xl overflow-hidden bg-gradient-to-br from-gov-ink via-gov-navy to-gov-blue text-white shadow-gov-lg">
      {/* Decorative layers */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.12]"
        style={{
          backgroundImage: `radial-gradient(circle, rgba(255,255,255,0.7) 1px, transparent 1px)`,
          backgroundSize: "22px 22px",
          maskImage: "linear-gradient(90deg, transparent 30%, black)",
          WebkitMaskImage: "linear-gradient(90deg, transparent 30%, black)",
        }}
      />
      <div className="absolute -right-16 -top-24 text-white/[0.07] pointer-events-none">
        <AshokaChakra size={320} strokeWidth={1} className="animate-spin-slow" />
      </div>
      <div className="absolute -left-16 -bottom-24 w-72 h-72 rounded-full bg-gov-saffron/20 blur-[90px] pointer-events-none" />

      <div className="relative z-10 px-6 md:px-8 py-7 flex flex-col md:flex-row md:items-center justify-between gap-6">

        {/* Left: Avatar + Info */}
        <div className="flex items-center gap-5 md:gap-6">
          {/* Avatar circle with tricolour ring */}
          <div className="relative w-20 h-20 rounded-full p-[3px] bg-[conic-gradient(#ff9933_0_33%,#ffffff_33%_66%,#138808_66%_100%)] flex-shrink-0 shadow-gov-lg">
            <div className="w-full h-full rounded-full bg-gov-navy flex items-center justify-center">
              <span className="text-3xl font-bold text-white">{initials}</span>
            </div>
            <span className="absolute bottom-0.5 right-0.5 w-5 h-5 rounded-full bg-gov-green border-2 border-gov-navy flex items-center justify-center">
              <BadgeCheck size={11} className="text-white" />
            </span>
          </div>

          {/* Text Info */}
          <div className="min-w-0">
            <div className="text-[11px] font-semibold text-gov-saffron mb-1 tracking-wide">Welcome back,</div>
            <div className="flex flex-wrap items-center gap-3 mb-1.5">
              <h1 className="text-[22px] md:text-[26px] font-bold tracking-tight leading-none">{displayName}</h1>
              <span className="flex items-center gap-1 text-[9.5px] font-bold uppercase tracking-wider text-[#86efac] bg-gov-green/25 border border-[#86efac]/40 px-2 py-0.5 rounded-full">
                <BadgeCheck size={11} />
                Verified Official
              </span>
            </div>
            <p className="text-white/80 text-[14px] font-medium mb-3">{profile.jobRole.title}</p>
            <div className="flex flex-wrap items-center gap-2 text-[11.5px] font-medium">
              <span className="flex items-center gap-1.5 bg-white/10 border border-white/10 rounded-full px-2.5 py-1">
                <User size={13} className="text-gov-saffron" /> {profile.govId}
              </span>
              <span className="flex items-center gap-1.5 bg-white/10 border border-white/10 rounded-full px-2.5 py-1">
                <Building2 size={13} className="text-gov-saffron" /> {profile.department}
              </span>
              <span className="flex items-center gap-1.5 bg-white/10 border border-white/10 rounded-full px-2.5 py-1">
                <Clock size={13} className="text-gov-saffron" /> Last assessed: {formatDate(profile.competencyProfile.lastEvaluatedDate)}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Ministry strapline + profile facts */}
        <div className="md:min-w-[250px] md:text-right">
          <p className="text-[15px] md:text-[16px] font-medium italic leading-snug text-white/90">
            “Data for a Stronger India<br className="hidden md:block" /> Through a More Competent Workforce”
          </p>
          <span className="mt-3 block h-[3px] w-14 rounded-full bg-gov-saffron md:ml-auto" />
          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-white/60 md:justify-end">
            <span>
              <CountUp end={totalAssessed} duration={900} className="font-bold text-white" /> competencies assessed
            </span>
            <span className="truncate font-mono tracking-wider">{profile.competencyProfile.profileId}</span>
          </div>
        </div>
      </div>
      <div className="tricolor-strip relative z-10" />
    </div>
  );
};

export default ProfileHeader;