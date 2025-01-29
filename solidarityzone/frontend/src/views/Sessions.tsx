import {
  ButtonGroup,
  Chip,
  Link,
  IconButton,
  Stack,
  TableCell,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import { Expand, Launch } from '@mui/icons-material';
import { Fragment, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { formatDateTime } from '~/utils';
import { Table } from '~/components/Table';
import { SessionDetailDialog } from '~/components/SessionDetailDialog';
import { usePaginationQuery } from '~/hooks';

import type { ScrapeSession } from '~/types';

const Sessions = () => {
  const { isLoading, result, handlePaginationChange } =
    usePaginationQuery<ScrapeSession>(`/api/sessions`);
  const [selected, setSelected] = useState<ScrapeSession | undefined>();

  const handleOpen = (caseId: number) => {
    const found = result?.items.find((item) => {
      return item.id === caseId;
    });

    setSelected(found ? found : undefined);
  };

  const handleClose = () => {
    setSelected(undefined);
  };

  return (
    <Fragment>
      {isLoading && !result ? (
        <Typography>Loading ...</Typography>
      ) : !result ? null : result.items.length === 0 ? (
        <Typography>No sessions found.</Typography>
      ) : (
        <Table
          columns={['Date', 'Court', 'Article', 'Cases', 'Result', 'Actions']}
          pagination={result.pagination}
          handlePaginationChange={handlePaginationChange}
        >
          {result.items.map((row) => (
            <TableRow key={row.id} hover>
              <TableCell scope="row">
                {formatDateTime(row.created_at)}
              </TableCell>
              <TableCell scope="row">
                {row.court ? (
                  <Link component={RouterLink} to={`/courts/${row.court.id}`}>
                    {row.court.name}
                  </Link>
                ) : (
                  row.input_court_code
                )}
              </TableCell>
              <TableCell scope="row">{row.input_article}</TableCell>
              <TableCell scope="row">
                <Stack direction="row" spacing={1}>
                  <Tooltip arrow title="New cases">
                    <Chip
                      label={row.created_cases}
                      color={row.created_cases > 0 ? 'secondary' : 'primary'}
                      size="small"
                    />
                  </Tooltip>
                  <Tooltip arrow title="Updated cases">
                    <Chip
                      label={row.updated_cases}
                      color={row.updated_cases > 0 ? 'info' : 'primary'}
                      size="small"
                    />
                  </Tooltip>
                  <Tooltip arrow title="Ignored cases">
                    <Chip
                      label={row.ignored_cases}
                      color="primary"
                      size="small"
                    />
                  </Tooltip>
                </Stack>
              </TableCell>
              <TableCell scope="row">
                {row.is_successful ? (
                  <Chip label="OK" color="success" size="small" />
                ) : (
                  <Chip label={row.error_type} color="error" size="small" />
                )}
              </TableCell>
              <TableCell scope="row">
                <ButtonGroup variant="outlined" size="small">
                  <IconButton component={RouterLink} to={`/sessions/${row.id}`}>
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
          ))}
        </Table>
      )}
      <SessionDetailDialog session={selected} handleClose={handleClose} />
    </Fragment>
  );
};

export default Sessions;
