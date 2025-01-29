import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { toPaginationParams } from '~/utils';
import { get } from '~/request';

import type { PaginationResult } from '~/types';

export function usePaginationQuery<T>(path: string) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PaginationResult<T> | undefined>();

  const handlePaginationChange = useCallback(
    (before?: string, after?: string, itemsPerPage?: number) => {
      setSearchParams(toPaginationParams({ before, after, itemsPerPage }));
    },
    [setSearchParams],
  );

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);

      try {
        const response = await get<PaginationResult<T>>(path, searchParams);
        setResult(response);
      } catch (error) {
        console.error(error);
        window.alert('Something went wrong ..');
      }

      setIsLoading(false);
    };

    fetchData();
  }, [path, searchParams]);

  return {
    isLoading,
    result,
    handlePaginationChange,
  };
}

export type FilterConfig = {
  [name: string]: {
    paramName: string;
    type?: 'string' | 'number[]' | 'string[]';
  };
};

export type FilterValues = string | number[] | string[] | null;

export function useFilterQuery<T, F extends Record<string, FilterValues>>(
  path: string,
  config: FilterConfig,
) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<T | undefined>();

  const handlePaginationChange = useCallback(
    (before?: string, after?: string, itemsPerPage?: number) => {
      setSearchParams((params) => {
        if (before) {
          params.set('before', before);
        } else {
          params.delete('before');
        }

        if (after) {
          params.set('after', after);
        } else {
          params.delete('after');
        }

        if (itemsPerPage) {
          params.set('itemsPerPage', itemsPerPage.toString());
        }

        return params;
      });
    },
    [setSearchParams],
  );

  const updateFilterParams = useCallback(
    (values: F) => {
      setSearchParams((previousParams) => {
        const params = new URLSearchParams();

        const itemsPerPage = previousParams.get('itemsPerPage');
        if (itemsPerPage) {
          params.set('itemsPerPage', itemsPerPage);
        }

        Object.keys(values).forEach((fieldName) => {
          if (!(fieldName in config)) {
            throw new Error(`Unknown filter param "${fieldName}"`);
          }

          const { paramName } = config[fieldName];
          const type = config[fieldName].type || 'string';

          if (type === 'string') {
            if (values[fieldName] !== null) {
              params.set(paramName, values[fieldName] as string);
            }
          } else if (
            Array.isArray(values[fieldName]) &&
            (type === 'number[]' || type === 'string[]')
          ) {
            if (values[fieldName] !== null) {
              for (const id of values[fieldName] as string[]) {
                params.append(paramName, id.toString());
              }
            }
          } else {
            throw new Error(`Invalid filter param "${fieldName}" type`);
          }
        });

        return params;
      });
    },
    [config, setSearchParams],
  );

  const clearParams = () => {
    setSearchParams();
  };

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);

      try {
        const response = await get<T>(path, searchParams);
        setResult(response);
      } catch (error) {
        console.error(error);
        window.alert('Something went wrong ..');
      }

      setIsLoading(false);
    };

    fetchData();
  }, [path, searchParams]);

  const filterParams = useMemo(() => {
    return Object.keys(config).reduce<Record<string, FilterValues>>(
      (acc, fieldName) => {
        const { paramName } = config[fieldName];
        const type = config[fieldName].type || 'string';

        if (type === 'number[]') {
          acc[fieldName] = searchParams
            .getAll(paramName)
            .map((value) => parseInt(value, 10));
        } else if (type === 'string[]') {
          acc[fieldName] = searchParams.getAll(paramName);
        } else if (type === 'string') {
          acc[fieldName] = searchParams.get(paramName) || null;
        }

        return acc;
      },
      {},
    );
  }, [config, searchParams]);

  return {
    clearParams,
    filterParams,
    isLoading,
    result,
    updateFilterParams,
    handlePaginationChange,
  };
}

export function useResolveIdQuery<T>(
  path: string,
  value: number[],
): [T[], boolean] {
  const [resolved, setResolved] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const resolve = async () => {
      setIsLoading(true);

      const params = new URLSearchParams(
        value.map((value) => ['id', value.toString()]),
      );

      const response = await window.fetch(`${path}?${params}`);
      const data: PaginationResult<T> = await response.json();
      setResolved(data.items);
      setIsLoading(false);
    };

    if (value.length > 0) {
      resolve();
    } else {
      setResolved([]);
    }
  }, [path, value]);

  return [resolved, isLoading];
}
