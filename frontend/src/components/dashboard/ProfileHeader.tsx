/**
 * FILE: src/components/dashboard/ProfileHeader.tsx
 * Handles partial profile data from backend gracefully.
 */

import React from 'react';
import { BadgeCheck, Briefcase, Clock, Building2, ShieldCheck } from 'lucide-react';
import type { Official } from '../../types/domain';

interface ProfileHeaderProps {
  profile: Official;
  totalAssessed: number;
}

const getInitials = (name: string): string =>
  name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 3);

const formatDate = (iso: string): string => {
  try {
    return new Date(iso).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  } catch {
    return 'N/A';
  }
};

const ProfileHeader: React.FC<ProfileHeaderProps> = ({ profile, totalAssessed }) => {
  // Gracefully handle partial data from the backend
  const displayName  = profile.fullName && profile.fullName !== 'MoSPI Official'
    ? profile.fullName
    : profile.govId;

  return (
    <div className="rounded-2xl overflow-hidden shadow-md border border-slate-200 dark:border-slate-800 transition-colors duration-200">
      {/* Tricolour accent */}
      <div className="flex h-1.5">
        <div className="flex-1 bg-orange-500" />
        <div className="flex-1 bg-white dark:bg-slate-800 border-y border-slate-200 dark:border-slate-700" />
        <div className="flex-1 bg-green-600" />
      </div>

      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 px-6 py-6">
        <div className="flex flex-col md:flex-row md:items-center gap-5">
          {/* Avatar */}
          <div className="flex-shrink-0">
            <div className="w-20 h-20 rounded-full bg-blue-700 border-4 border-blue-500/40 flex items-center justify-center shadow-inner">
              <span className="text-white font-bold text-2xl tracking-wide">
                {getInitials(displayName)}
              </span>
            </div>
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h1 className="text-white text-2xl font-bold tracking-tight truncate">
                {displayName}
              </h1>
              <span className="flex items-center gap-1 text-xs bg-blue-700/60 text-blue-200 px-2 py-0.5 rounded-full border border-blue-600/40">
                <ShieldCheck size={11} /> Verified Official
              </span>
            </div>
            <p className="text-blue-300 text-sm font-medium mb-3">
              {profile.jobRole.title}
            </p>

            <div className="flex flex-wrap gap-3 text-xs text-slate-400 dark:text-slate-500">
              <span className="flex items-center gap-1.5">
                <BadgeCheck size={13} className="text-blue-400" />
                <span className="font-mono text-blue-300">{profile.govId}</span>
              </span>
              <span className="flex items-center gap-1.5">
                <Building2 size={13} /> {profile.department}
              </span>
              {profile.experienceYears > 0 && (
                <span className="flex items-center gap-1.5">
                  <Briefcase size={13} /> {profile.experienceYears} yrs experience
                </span>
              )}
              <span className="flex items-center gap-1.5">
                <Clock size={13} /> Last assessed:{' '}
                {formatDate(profile.competencyProfile.lastEvaluatedDate)}
              </span>
            </div>
          </div>

          {/* Stat Pills */}
          <div className="flex flex-row md:flex-col gap-3 md:gap-2 flex-shrink-0">
            <StatPill label="Competencies Assessed" value={totalAssessed} color="blue" />
            <StatPill
              label="Profile ID"
              value={profile.competencyProfile.profileId}
              color="slate"
              mono
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const StatPill: React.FC<{
  label: string;
  value: string | number;
  color: 'blue' | 'slate';
  mono?: boolean;
}> = ({ label, value, color, mono }) => {
  const palette =
    color === 'blue'
      ? 'bg-blue-800/50 dark:bg-blue-900/40 border-blue-700/40 text-blue-100'
      : 'bg-slate-800/60 dark:bg-slate-800/40 border-slate-700/40 text-slate-300';
  return (
    <div className={`rounded-xl border px-4 py-2 text-center transition-colors ${palette}`}>
      <div className={`text-base font-bold ${mono ? 'font-mono text-sm' : ''}`}>{value}</div>
      <div className="text-xs opacity-70 mt-0.5 whitespace-nowrap">{label}</div>
    </div>
  );
};

export default ProfileHeader;
