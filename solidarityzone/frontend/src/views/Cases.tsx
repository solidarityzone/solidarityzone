import { Paper, Typography } from '@mui/material';
import { Fragment, useCallback, useEffect, useState } from 'react';

import { CasesFilter, CasesFilterValues } from '~/components/CasesFilter';
import { CasesTable } from '~/components/CasesTable';
import { FilterConfig, useFilterQuery } from '~/hooks';

import type { Case, PaginationResult } from '~/types';

const defaultValues: CasesFilterValues = {
  articles: [],
  courts: [],
  defendants: [],
  judges: [],
  regions: [],
  entryDateFrom: null,
  entryDateTo: null,
  resultDateFrom: null,
  resultDateTo: null,
  effectiveDateFrom: null,
  effectiveDateTo: null,
};

const filterConfig: FilterConfig = {
  articles: {
    paramName: 'article',
    type: 'string[]',
  },
  courts: {
    paramName: 'court',
    type: 'number[]',
  },
  defendants: {
    paramName: 'defendant',
    type: 'string[]',
  },
  judges: {
    paramName: 'judge',
    type: 'string[]',
  },
  regions: {
    paramName: 'region',
    type: 'number[]',
  },
  entryDateFrom: {
    paramName: 'from',
    type: 'string',
  },
  entryDateTo: {
    paramName: 'to',
    type: 'string',
  },
  resultDateFrom: {
    paramName: 'rfrom',
    type: 'string',
  },
  resultDateTo: {
    paramName: 'rto',
    type: 'string',
  },
  effectiveDateFrom: {
    paramName: 'ecfrom',
    type: 'string',
  },
  effectiveDateTo: {
    paramName: 'ecto',
    type: 'string',
  },
};

const Cases = () => {
  const {
    clearParams,
    filterParams,
    isLoading,
    result,
    updateFilterParams,
    handlePaginationChange,
  } = useFilterQuery<PaginationResult<Case>, CasesFilterValues>(
    '/api/cases',
    filterConfig,
  );

  const [filterValues, setFilterValues] = useState({
    ...defaultValues,
    ...filterParams,
  });

  const handleFilterChange = useCallback((values: CasesFilterValues) => {
    setFilterValues(values);
  }, []);

  const handleSubmit = () => {
    updateFilterParams(filterValues);
  };

  const handleClear = () => {
    setFilterValues(defaultValues);
    clearParams();
  };

  useEffect(() => {
    setFilterValues(filterParams as CasesFilterValues);
  }, [filterParams]);

  return (
    <Fragment>
      <Paper elevation={1} sx={{ p: 2 }}>
        <CasesFilter
          disabled={isLoading}
          onSubmit={handleSubmit}
          onChange={handleFilterChange}
          onClear={handleClear}
          values={filterValues}
        />
      </Paper>
      <br />
      {isLoading && !result ? (
        <Typography>Searching ...</Typography>
      ) : !result ? null : result.items.length === 0 ? (
        <Typography>No results found.</Typography>
      ) : (
        <CasesTable
          result={result}
          handlePaginationChange={handlePaginationChange}
        />
      )}
    </Fragment>
  );
};

export default Cases;
