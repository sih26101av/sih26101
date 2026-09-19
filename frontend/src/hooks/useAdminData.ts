/**
 * FILE: src/hooks/useAdminData.ts
 *
 * Admin console data hooks. KPIs, the shortage heatmap, departmental
 * compliance and roster pages are computed on the server
 * (/api/v1/admin/console/*, routers/admin_console.py) — the browser no longer
 * downloads and aggregates the whole roster. Every hook takes the shared
 * department / grade / office filters.
 */

import { useCallback, useEffect, useState } from 'react';
import {
  fetchAdminFacets, fetchAdminOverview, fetchAdminRoster,
  type AdminFacets, type AdminFilters, type AdminOverview, type AdminRosterRow, type Page, type StatusCounts,
} from '../services/api';

export type { AdminRosterRow } from '../services/api';

export interface AsyncState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

/** Load `fn` whenever `key` changes (or on refetch); stale responses are dropped. */
export function useAsync<T>(fn: () => Promise<T>, key: string): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  const refetch = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fn()
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Request failed');
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, tick]);

  return { data, isLoading, error, refetch };
}

export const filterKey = (f: AdminFilters) => `${f.department ?? ''}|${f.grade ?? ''}|${f.office ?? ''}`;

export function useAdminFacets(): AsyncState<AdminFacets> {
  return useAsync(fetchAdminFacets, 'facets');
}

/** KPIs + status counts + heatmap + departmental compliance for the filtered workforce. */
export function useAdminOverview(filters: AdminFilters): AsyncState<AdminOverview> {
  return useAsync(() => fetchAdminOverview(filters), filterKey(filters));
}

/** One server-side page of the roster. */
export function useAdminRoster(
  filters: AdminFilters, page: number, pageSize: number, search: string, status: 'all' | 0 | 1 | 2,
): AsyncState<Page<AdminRosterRow> & { statusCounts: StatusCounts }> {
  const st = status === 'all' ? undefined : status;
  return useAsync(
    () => fetchAdminRoster(filters, page, pageSize, search, st),
    `${filterKey(filters)}|${page}|${pageSize}|${search}|${status}`,
  );
}
