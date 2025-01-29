import { Link, Paper, TableCell, TableRow, Typography } from '@mui/material';
import { Fragment, useCallback, useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { CourtsFilter, CourtsFilterValue } from '~/components/CourtsFilter';
import { Table } from '~/components/Table';
import { FilterConfig, useFilterQuery } from '~/hooks';

import type { Court, PaginationResult } from '~/types';

const defaultValues: CourtsFilterValue = {
  regions: [],
};

const filterConfig: FilterConfig = {
  regions: {
    paramName: 'region',
    type: 'number[]',
  },
};

const Courts = () => {
  const {
    clearParams,
    filterParams,
    isLoading,
    result,
    updateFilterParams,
    handlePaginationChange,
  } = useFilterQuery<PaginationResult<Court>, CourtsFilterValue>(
    '/api/courts',
    filterConfig,
  );

  const [filterValues, setFilterValues] = useState({
    ...defaultValues,
    ...filterParams,
  });

  const handleFilterChange = useCallback((values: CourtsFilterValue) => {
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
    setFilterValues(filterParams as CourtsFilterValue);
  }, [filterParams]);

  return (
    <Fragment>
      <Paper elevation={1} sx={{ p: 2 }}>
        <CourtsFilter
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
        <Table
          columns={['Name', 'Code', 'Region']}
          pagination={result.pagination}
          handlePaginationChange={handlePaginationChange}
        >
          {result.items.map((row) => (
            <TableRow key={row.id} hover>
              <TableCell scope="row">
                <Link component={RouterLink} to={`/courts/${row.id}`}>
                  {row.name}
                </Link>
              </TableCell>
              <TableCell scope="row">{row.code}</TableCell>
              <TableCell scope="row">{row.region.name}</TableCell>
            </TableRow>
          ))}
        </Table>
      )}
    </Fragment>
  );
};

export default Courts;
