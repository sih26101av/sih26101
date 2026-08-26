/**
 * FILE: src/services/chatApi.ts
 *
 * Chatbot API service — sends messages to the Gyan AI backend endpoint.
 * Archit Shukla | MoSPI Skill Intelligence Platform | SIH 2026
 */

import type { SkillGapEntry, CourseRecommendation } from '../types/domain';

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  content: string;
  timestamp: Date;
  detectedLanguage?: 'en' | 'hi';
}

interface ChatApiPayload {
  user_id: string;
  message: string;
  history: { role: string; content: string }[];
  job_role: string;
  department: string;
  skill_gaps: {
    skillName: string;
    domain: string;
    currentLevel: number;
    targetLevel: number;
    gapScore: number;
  }[];
  recommendations: {
    title: string;
    provider: string;
    durationHours: number;
    matchReason: string;
  }[];
}

interface ChatApiResponse {
  reply: string;
  detected_language: string;
}

export async function sendChatMessage(
  officialId: string,
  message: string,
  history: ChatMessage[],
  jobRole: string,
  department: string,
  skillGaps: SkillGapEntry[],
  recommendations: CourseRecommendation[]
): Promise<{ reply: string; detectedLanguage: 'en' | 'hi' }> {
  const payload: ChatApiPayload = {
    user_id: officialId,
    message,
    history: history.map(m => ({ role: m.role, content: m.content })),
    job_role: jobRole,
    department,
    skill_gaps: skillGaps.map(g => ({
      skillName: g.competency.skillName,
      domain: g.competency.domain,
      currentLevel: g.currentLevel,
      targetLevel: g.requiredLevel,
      gapScore: g.gap,
    })),
    recommendations: recommendations.map(r => ({
      title: r.course.title,
      provider: r.course.source,
      durationHours: r.course.durationHours,
      matchReason: r.aiMatchTag,
    })),
  };

  const res = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Chat API error: ${res.status} ${res.statusText}`);
  }

  const data: ChatApiResponse = await res.json();
  return {
    reply: data.reply,
    detectedLanguage: (data.detected_language as 'en' | 'hi') ?? 'en',
  };
}
