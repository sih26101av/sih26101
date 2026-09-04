/**
 * FILE: src/hooks/useChatEngine.ts
 *
 * Shared chat engine hook — used by both ChatWidget (dashboard) and
 * HomeChatWidget (landing page). Contains all message state, send logic,
 * auto-scroll, typing indicator, and language detection.
 *
 * Archit Shukla | SIH 2026
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import type { SkillGapEntry, CourseRecommendation } from '../types/domain';
import { sendChatMessage, type ChatMessage, type NavigateAction } from '../services/chatApi';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface PendingNavAction {
  action: NavigateAction;
  confirming: boolean;
}

export interface UseChatEngineOptions {
  officialId: string;
  jobRole?: string;
  department?: string;
  fullName?: string;
  govId?: string;
  skillGaps?: SkillGapEntry[];
  recommendations?: CourseRecommendation[];
  context?: 'dashboard' | 'home';
  lang: 'en' | 'hi';
  onNavigate?: (action: NavigateAction) => void;
}

export interface UseChatEngineReturn {
  messages: ChatMessage[];
  isTyping: boolean;
  pendingNav: PendingNavAction | null;
  handleSend: (text: string) => void;
  confirmNav: () => void;
  cancelNav: () => void;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useChatEngine({
  officialId,
  jobRole = 'Statistical Official',
  department = 'MoSPI',
  fullName,
  govId,
  skillGaps = [],
  recommendations = [],
  context = 'dashboard',
  lang,
  onNavigate,
}: UseChatEngineOptions): UseChatEngineReturn {
  const [messages, setMessages]       = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping]       = useState(false);
  const [pendingNav, setPendingNav]   = useState<PendingNavAction | null>(null);
  const messagesEndRef                = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isTyping) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const { reply, detectedLanguage, navigateAction } = await sendChatMessage(
        officialId, trimmed, messages,
        jobRole, department, skillGaps, recommendations,
        fullName, govId, context,
      );

      await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 500));

      const botMsg: ChatMessage = {
        id: `msg-${Date.now()}-bot`,
        role: 'model',
        content: reply,
        timestamp: new Date(),
        detectedLanguage,
      };
      setMessages(prev => [...prev, botMsg]);

      // If backend returned a navigation action, hold it for confirmation
      if (navigateAction) {
        setPendingNav({ action: navigateAction, confirming: true });
      }
    } catch {
      const errMsg: ChatMessage = {
        id: `msg-err-${Date.now()}`,
        role: 'model',
        content: lang === 'hi'
          ? 'Maafi chahta hoon, abhi kuch technical problem aa gayi. Thodi der baad try karein. 🙏'
          : 'Sorry, I ran into a technical issue. Please try again in a moment. 🙏',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [isTyping, messages, officialId, jobRole, department, fullName, govId, skillGaps, recommendations, context, lang]);

  const confirmNav = useCallback(() => {
    if (!pendingNav) return;
    onNavigate?.(pendingNav.action);
    setPendingNav(null);
  }, [pendingNav, onNavigate]);

  const cancelNav = useCallback(() => {
    setPendingNav(null);
  }, []);

  return { messages, isTyping, pendingNav, handleSend, confirmNav, cancelNav, messagesEndRef };
}
