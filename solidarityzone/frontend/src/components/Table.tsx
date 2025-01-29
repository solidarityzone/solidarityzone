import {
  Paper,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Table as MaterialTable,
  SelectChangeEvent,
} from '@mui/material';
import { Fragment, ReactNode } from 'react';

import { Pagination } from '~/components/Pagination';

import type { PaginationInfo } from '~/types';

export type TableProps = {
  handlePaginationChange: (
    before?: string,
    after?: string,
    itemsPerPage?: number,
  ) => void;
  columns: string[];
  pagination: PaginationInfo;
  children: ReactNode;
};

export const Table = ({
  columns,
  children,
  pagination,
  handlePaginationChange,
}: TableProps) => {
  const handleChangeRowsPerPage = (event: SelectChangeEvent<number>) => {
    handlePaginationChange(
      undefined,
      undefined,
      parseInt(event.target.value.toString(), 10),
    );
  };

  const handleNextPage = () => {
    handlePaginationChange(
      undefined,
      pagination.endCursor,
      pagination.itemsPerPage,
    );
  };

  const handlePreviousPage = () => {
    handlePaginationChange(
      pagination.startCursor,
      undefined,
      pagination.itemsPerPage,
    );
  };

  return (
    <Fragment>
      <Paper elevation={1}>
        <Pagination
          totalItems={pagination.totalItems}
          rowsPerPageOptions={[10, 25, 50, 75, 100]}
          rowsPerPage={pagination.itemsPerPage}
          onNextPage={handleNextPage}
          onPreviousPage={handlePreviousPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          hasNextPage={pagination.hasNextPage}
          hasPreviousPage={pagination.hasPreviousPage}
        />
        <TableContainer>
          <MaterialTable>
            <TableHead>
              <TableRow>
                {columns.map((column) => {
                  return (
                    <TableCell key={column}>
                      <strong>{column}</strong>
                    </TableCell>
                  );
                })}
              </TableRow>
            </TableHead>
            <TableBody>{children}</TableBody>
          </MaterialTable>
        </TableContainer>
        <Pagination
          totalItems={pagination.totalItems}
          rowsPerPageOptions={[10, 25, 50, 75, 100]}
          rowsPerPage={pagination.itemsPerPage}
          onNextPage={handleNextPage}
          onPreviousPage={handlePreviousPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          hasNextPage={pagination.hasNextPage}
          hasPreviousPage={pagination.hasPreviousPage}
        />
      </Paper>
    </Fragment>
  );
};
