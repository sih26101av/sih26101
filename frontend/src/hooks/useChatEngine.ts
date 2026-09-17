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
import { sendChatMessage, type ChatLanguage, type ChatMessage, type NavigateAction } from '../services/chatApi';
import { chatCopy } from '../i18n/chatLanguages';

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
  lang: ChatLanguage;
  onNavigate?: (action: NavigateAction) => void;
  onThemeToggle?: (target: 'dark' | 'light' | 'toggle') => void;
  onLanguageChange?: (target: ChatLanguage) => void;
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
  onThemeToggle,
  onLanguageChange,
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
      const { reply, detectedLanguage, navigateAction, navigateActions } = await sendChatMessage(
        officialId, trimmed, messages,
        jobRole, department, skillGaps, recommendations,
        fullName, govId, context,
        lang,   // widget language — used when the message itself gives no signal
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

      // Compound actions (navigate_actions array) — execute all immediately
      if (navigateActions.length > 0) {
        for (const action of navigateActions) {
          if (action.type === 'theme') {
            onThemeToggle?.(action.target as 'dark' | 'light' | 'toggle');
          } else if (action.type === 'language') {
            onLanguageChange?.(action.target as ChatLanguage);
          } else if (action.type !== 'scroll' && action.type !== 'modal') {
            // Other non-confirmation actions: ignore for now
          }
        }
      }
      // Single action (navigate_action) — existing flow
      // Theme action → execute immediately, no confirmation needed
      if (navigateAction?.type === 'theme') {
        onThemeToggle?.(navigateAction.target as 'dark' | 'light' | 'toggle');
      } else if (navigateAction?.type === 'language') {
        onLanguageChange?.(navigateAction.target as ChatLanguage);
      } else if (navigateAction) {
        // All other navigation actions → show confirmation dialog
        setPendingNav({ action: navigateAction, confirming: true });
      }
    } catch {
      const errMsg: ChatMessage = {
        id: `msg-err-${Date.now()}`,
        role: 'model',
        content: chatCopy(lang).error,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [isTyping, messages, officialId, jobRole, department, fullName, govId, skillGaps, recommendations, context, lang, onThemeToggle, onLanguageChange]);

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
