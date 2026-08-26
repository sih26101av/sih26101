/**
 * FILE: src/patterns/DashboardFactory.ts
 *
 * PATTERN: Factory Method Pattern
 * ─────────────────────────────────────────────────────────────────────────────
 * PURPOSE:
 *   Decouples the LandingPage's routing logic from the concrete dashboard
 *   components. Instead of importing and hard-coding <LearnerDashboard> or
 *   <AdminDashboard> directly, the landing page asks the factory for the
 *   correct *route path* based on the user's role. The factory then registers
 *   the matching React component and route against a central registry.
 *
 * SOLID PRINCIPLES APPLIED:
 *   - OCP (Open/Closed): Adding a new role (e.g., "trainer") only requires
 *     registering a new creator in the registry — zero changes to callers.
 *   - DIP (Dependency Inversion): Callers depend only on IDashboard, never
 *     on concrete dashboard components.
 *   - SRP (Single Responsibility): The factory is solely responsible for
 *     resolving which dashboard to render for a given user role.
 *
 * MERMAID ALIGNMENT:
 *   Directly implements the Factory Pattern described in ARCHITECTURE.md §4.C
 *   and the UserRole enum from mospi-competency-platform.mermaid.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import React from 'react';

// ─── UserRole Enum (mirrors mospi-competency-platform.mermaid BaseUser.role) ──
export type UserRole = 'official' | 'admin' | 'trainer';

// ─── Product Interface ────────────────────────────────────────────────────────
export interface IDashboard {
  /** The React component to render for this dashboard. */
  component: React.ComponentType<DashboardProps>;
  /** The route path this dashboard lives at. */
  routePath: string;
  /** Human-readable label used for redirect messages, tab titles, etc. */
  label: string;
}

export interface DashboardProps {
  officialId?: string;
}

// ─── Abstract Creator ─────────────────────────────────────────────────────────
abstract class DashboardCreator {
  /** Factory method — subclasses override this to produce a concrete product. */
  abstract createDashboard(): IDashboard;

  /**
   * Template method — any pre-navigation logic (analytics, auth checks, etc.)
   * can be inserted here without touching callers.
   */
  navigate(officialId?: string): string {
    const dashboard = this.createDashboard();
    const path = officialId
      ? `${dashboard.routePath}/${officialId}`
      : dashboard.routePath;
    return path;
  }
}

// ─── Concrete Creators ────────────────────────────────────────────────────────

class OfficialDashboardCreator extends DashboardCreator {
  private userId: string;
  constructor(userId: string = 'usr_720465595') {  // Gabriel Manda — first user in users.json
    super();
    this.userId = userId;
  }

  createDashboard(): IDashboard {
    const component = React.lazy(() => import('../pages/LearnerDashboard'));
    return {
      component: component as unknown as React.ComponentType<DashboardProps>,
      routePath: `/dashboard`,
      label: 'Official Dashboard',
    };
  }

  navigate(): string {
    return `/dashboard/${this.userId}`;
  }
}

class AdminDashboardCreator extends DashboardCreator {
  createDashboard(): IDashboard {
    const component = React.lazy(() => import('../pages/AdminDashboard'));
    return {
      component: component as unknown as React.ComponentType<DashboardProps>,
      routePath: `/admin`,
      label: 'Admin Dashboard',
    };
  }

  navigate(): string {
    return this.createDashboard().routePath;
  }
}

// ─── Placeholder for future Trainer role ─────────────────────────────────────
class TrainerDashboardCreator extends DashboardCreator {
  private userId: string;
  constructor(userId: string = 'usr_720465595') {
    super();
    this.userId = userId;
  }

  createDashboard(): IDashboard {
    const component = React.lazy(() => import('../pages/LearnerDashboard'));
    return {
      component: component as unknown as React.ComponentType<DashboardProps>,
      routePath: `/trainer`,
      label: 'Trainer Dashboard',
    };
  }

  navigate(): string {
    return `/trainer/${this.userId}`;
  }
}

// ─── The Factory ──────────────────────────────────────────────────────────────
/**
 * DashboardFactory
 * ────────────────
 * The single entry point for all callers. It maintains a registry of role →
 * creator mappings. Callers only ever interact with this class; they never
 * touch any of the concrete creators above.
 *
 * Usage:
 *   const path = DashboardFactory.getNavigationPath('official', 'EMP-8472');
 *   navigate(path); // React Router navigate
 */
export class DashboardFactory {
  private static registry: Map<UserRole, (userId?: string) => DashboardCreator> = new Map<UserRole, (userId?: string) => DashboardCreator>([
    ['official', (userId?: string) => new OfficialDashboardCreator(userId)],
    ['admin',    (_userId?: string) => new AdminDashboardCreator()],
    ['trainer',  (userId?: string) => new TrainerDashboardCreator(userId)],
  ]);

  /**
   * Returns the React Router path for a given role.
   * @param role   - The user's role
   * @param userId - Real userId from the mock server (e.g. 'usr_720465595')
   */
  static getNavigationPath(role: UserRole, userId?: string): string {
    const creatorFactory = this.registry.get(role);
    if (!creatorFactory) {
      console.error(`[DashboardFactory] Unknown role: "${role}". Falling back to landing.`);
      return '/';
    }
    const creator = creatorFactory(userId);
    return creator.navigate(userId);
  }

  /**
   * Returns the full IDashboard product for a given role.
   * Used by the router in App.tsx to register lazy-loaded routes.
   */
  static getDashboard(role: UserRole): IDashboard | null {
    const creatorFactory = this.registry.get(role);
    if (!creatorFactory) return null;
    return creatorFactory().createDashboard();
  }

  /**
   * Registers a new creator for a previously unknown role.
   * Enables the OCP: new roles can be added at runtime without modifying
   * this file.
   */
  static register(role: UserRole, creatorFn: () => DashboardCreator): void {
    this.registry.set(role, creatorFn);
  }
}
