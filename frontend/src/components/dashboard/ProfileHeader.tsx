/**
 * FILE: src/components/dashboard/ProfileHeader.tsx
 */

import React from "react";
import { BadgeCheck, Building2, Clock, User } from "lucide-react";
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

const ProfileHeader: React.FC<ProfileHeaderProps> = ({ profile, totalAssessed }) => {
  const displayName = profile.fullName && profile.fullName !== "MoSPI Official" ? profile.fullName : profile.govId;
  const initials = displayName.substring(0, 1).toUpperCase();

  return (
    <div className="relative bg-white dark:bg-slate-800/40 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none overflow-hidden transition-colors duration-300">
      
      {/* Blue top line */}
      <div className="absolute top-0 left-0 right-0 h-[6px] bg-[#3b82f6]" />

      {/* Dotted circuit background — right 60% */}
      <div
        className="absolute top-0 right-0 w-[60%] h-full pointer-events-none opacity-[0.2] dark:opacity-[0.05] transition-opacity duration-300"
        style={{
          backgroundImage: `radial-gradient(circle, #94a3b8 1px, transparent 1px)`,
          backgroundSize: "22px 22px",
        }}
      />

      <div className="relative z-10 px-8 py-7 flex flex-col md:flex-row md:items-center justify-between gap-6">
        
        {/* Left: Avatar + Info */}
        <div className="flex items-center gap-6">
          {/* Avatar circle */}
          <div className="w-20 h-20 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center flex-shrink-0 shadow-sm dark:shadow-none transition-colors duration-300">
            <span className="text-slate-700 dark:text-slate-300 font-medium text-3xl transition-colors duration-300">{initials}</span>
          </div>

          {/* Text Info */}
          <div>
            <div className="flex items-center gap-3 mb-1.5">
              <h1 className="text-slate-900 dark:text-white font-extrabold text-[24px] tracking-tight leading-none transition-colors duration-300">{displayName}</h1>
              <span className="flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider bg-[#eff6ff] dark:bg-blue-900/30 text-[#3b82f6] dark:text-blue-400 border border-[#bfdbfe] dark:border-blue-900/50 px-2 py-0.5 rounded-full transition-colors duration-300">
                <BadgeCheck size={11} className="text-[#3b82f6] dark:text-blue-400" />
                Verified Official
              </span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-[14px] font-medium mb-3 transition-colors duration-300">{profile.jobRole.title}</p>
            <div className="flex flex-wrap items-center gap-5 text-[12px] text-slate-500 font-medium">
              <span className="flex items-center gap-1.5">
                <User size={14} className="text-slate-400 dark:text-slate-500" /> <span className="dark:text-slate-300">{profile.govId}</span>
              </span>
              <span className="flex items-center gap-1.5">
                <Building2 size={14} className="text-slate-400 dark:text-slate-500" /> <span className="dark:text-slate-300">{profile.department}</span>
              </span>
              <span className="flex items-center gap-1.5">
                <Clock size={14} className="text-slate-400 dark:text-slate-500" /> <span className="dark:text-slate-300">Last assessed: {formatDate(profile.competencyProfile.lastEvaluatedDate)}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Right: Stat Boxes */}
        <div className="flex flex-row md:flex-col gap-3 md:min-w-[180px]">
          <div className="bg-[#fafafa] dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50 rounded-[16px] px-4 py-3 flex flex-col items-center justify-center shadow-sm dark:shadow-none flex-1 md:flex-initial transition-colors duration-300">
            <span className="text-slate-900 dark:text-white text-[20px] font-black leading-none transition-colors duration-300">{totalAssessed}</span>
            <span className="text-slate-500 dark:text-slate-400 text-[11px] font-medium mt-1 text-center transition-colors duration-300">Competencies Assessed</span>
          </div>
          <div className="bg-[#fafafa] dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50 rounded-[16px] px-4 py-3 flex flex-col items-center justify-center shadow-sm dark:shadow-none flex-1 md:flex-initial transition-colors duration-300">
            <span className="text-slate-800 dark:text-slate-200 text-[13px] font-bold font-mono tracking-wider leading-none transition-colors duration-300">{profile.competencyProfile.profileId}</span>
            <span className="text-slate-500 dark:text-slate-400 text-[11px] font-medium mt-1 text-center transition-colors duration-300">Profile ID</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileHeader;