import { Typography } from '@mui/material';

import { CourtHistoryTable } from '~/components/CourtHistoryTable';
import { usePaginationQuery } from '~/hooks';

import type { ScrapeLog } from '~/types';

type Props = {
  id: string;
};

export const CourtHistory = ({ id }: Props) => {
  const { isLoading, result, handlePaginationChange } =
    usePaginationQuery<ScrapeLog>(`/api/courts/${id}/history`);

  return isLoading && !result ? (
    <Typography>Loading ...</Typography>
  ) : !result ? null : result.items.length === 0 ? (
    <Typography>No history found.</Typography>
  ) : (
    <CourtHistoryTable
      result={result}
      handlePaginationChange={handlePaginationChange}
    />
  );
};
