import { useState, useEffect, useCallback } from 'react';

interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useFetch<T>(url: string, options?: RequestInit) {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async (abortController?: AbortController, isRefetch = false) => {
    if (isRefetch) {
      setState((prev) => ({ ...prev, loading: true, error: null }));
    }
    try {
      const response = await fetch(url, { 
        ...options,
        signal: abortController?.signal 
      });
      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }
      const json = await response.json();
      setState({ data: json, loading: false, error: null });
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      if (err.name !== 'AbortError') {
        setState({ data: null, loading: false, error: err });
      }
    }
  }, [url]);

  useEffect(() => {
    const abortController = new AbortController();
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData(abortController, false);

    return () => {
      abortController.abort();
    };
  }, [fetchData]);

  return { ...state, refetch: () => fetchData(undefined, true) };
}
