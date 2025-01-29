import { Chip, Link, TableCell, TableRow } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

import { formatDate, formatDateTime } from '~/utils';
import { Table } from '~/components/Table';

import type { PaginationResult, ScrapeLog } from '~/types';

type Props = {
  result: PaginationResult<ScrapeLog>;
  handlePaginationChange: (
    before?: string,
    after?: string,
    itemsPerPage?: number,
  ) => void;
};

export const CourtHistoryTable = ({
  result,
  handlePaginationChange,
}: Props) => {
  return (
    <Table
      columns={['Scrape Date', 'Case', 'Type']}
      pagination={result.pagination}
      handlePaginationChange={handlePaginationChange}
    >
      {result.items.map((row) => (
        <TableRow key={row.id} hover>
          <TableCell scope="row">
            <Link
              component={RouterLink}
              to={`/sessions/${row.scrape_session_id}`}
            >
              {formatDateTime(row.created_at)}
            </Link>
          </TableCell>
          <TableCell scope="row">
            <Link component={RouterLink} to={`/cases/${row.case.id}`}>
              {row.case.defendant_name}
            </Link>{' '}
            ({formatDate(row.case.entry_date)})
          </TableCell>
          <TableCell scope="row">
            {row.is_update ? (
              <Chip label="Updated case" color="info" size="small" />
            ) : (
              <Chip label="New case" color="secondary" size="small" />
            )}
          </TableCell>
        </TableRow>
      ))}
    </Table>
  );
};
