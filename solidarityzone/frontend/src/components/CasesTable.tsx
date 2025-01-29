import { Expand, Launch } from '@mui/icons-material';
import {
  ButtonGroup,
  IconButton,
  Link,
  TableCell,
  TableRow,
} from '@mui/material';
import { Fragment, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { formatDate } from '~/utils';
import { Table } from '~/components/Table';
import { CaseDetailDialog } from '~/components/CaseDetailDialog';

import type { Case, PaginationResult } from '~/types';

type RowProps = {
  row: Case;
  handleOpen: (caseId: number) => void;
};

const CaseRow = ({ row, handleOpen }: RowProps) => {
  return (
    <TableRow hover>
      <TableCell scope="row">{formatDate(row.entry_date)}</TableCell>
      <TableCell scope="row">{formatDate(row.result_date)}</TableCell>
      <TableCell scope="row">{formatDate(row.effective_date)}</TableCell>
      <TableCell scope="row">{row.defendant_name}</TableCell>
      <TableCell scope="row">
        <Link component={RouterLink} to={`/courts/${row.court.id}`}>
          {row.court.name}
        </Link>
        {' ('}
        <Link component={RouterLink} to={`/courts?region=${row.region.id}`}>
          {row.region.name}
        </Link>
        {')'}
      </TableCell>
      <TableCell scope="row">{row.articles}</TableCell>
      <TableCell scope="row">
        <ButtonGroup variant="outlined" size="small">
          <IconButton component={RouterLink} to={`/cases/${row.id}`}>
            <Launch />
          </IconButton>
          <IconButton
            onClick={() => {
              handleOpen(row.id);
            }}
          >
            <Expand />
          </IconButton>
        </ButtonGroup>
      </TableCell>
    </TableRow>
  );
};

type Props = {
  result: PaginationResult<Case>;
  handlePaginationChange: (
    before?: string,
    after?: string,
    itemsPerPage?: number,
  ) => void;
};

export const CasesTable = ({ result, handlePaginationChange }: Props) => {
  const [selected, setSelected] = useState<Case | undefined>();

  const handleOpen = (caseId: number) => {
    const found = result.items.find((item) => {
      return item.id === caseId;
    });

    setSelected(found ? found : undefined);
  };

  const handleClose = () => {
    setSelected(undefined);
  };

  return (
    <Fragment>
      <Table
        columns={[
          'Entry Date',
          'Result Date',
          'Effective Date',
          'Defendant',
          'Court',
          'Articles',
          'Actions',
        ]}
        pagination={result.pagination}
        handlePaginationChange={handlePaginationChange}
      >
        {result.items.map((row) => (
          <CaseRow key={`${row.id}`} row={row} handleOpen={handleOpen} />
        ))}
      </Table>
      <CaseDetailDialog selected={selected} handleClose={handleClose} />
    </Fragment>
  );
};
