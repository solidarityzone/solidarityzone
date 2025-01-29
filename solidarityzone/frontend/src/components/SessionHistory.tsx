import { Typography } from '@mui/material';

import { CaseHistoryTable } from '~/components/CaseHistoryTable';
import { usePaginationQuery } from '~/hooks';

import type { ScrapeLog } from '~/types';

type Props = {
  id: string;
};

export const SessionHistory = ({ id }: Props) => {
  const { isLoading, result, handlePaginationChange } =
    usePaginationQuery<ScrapeLog>(`/api/sessions/${id}/history`);

  return isLoading && !result ? (
    <Typography>Loading ...</Typography>
  ) : !result ? null : result.items.length === 0 ? (
    <Typography>No history found.</Typography>
  ) : (
    <CaseHistoryTable
      result={result}
      handlePaginationChange={handlePaginationChange}
    />
  );
};
