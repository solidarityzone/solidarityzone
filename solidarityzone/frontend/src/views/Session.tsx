import { Radar } from '@mui/icons-material';
import { Typography } from '@mui/material';
import { Fragment, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import { DebugMessage } from '~/components/DebugMessage';
import { SessionDetail } from '~/components/SessionDetail';
import { SessionHistory } from '~/components/SessionHistory';
import { formatDateTime } from '~/utils';
import { get } from '~/request';

import type { ScrapeSession } from '~/types';

const Session = () => {
  const [data, setData] = useState<ScrapeSession | undefined>();
  const { id } = useParams();

  useEffect(() => {
    const fetchData = async () => {
      if (!id) {
        return;
      }

      const response = await get<ScrapeSession>(`/api/sessions/${id}`);
      setData(response);
    };

    fetchData();
  }, [id]);

  return !data || !id ? (
    <Typography>Loading ...</Typography>
  ) : (
    <Fragment>
      <Typography mb={2} variant="h5">
        <Radar /> {formatDateTime(data.created_at)} (
        {data.court ? data.court.name : data.input_court_code})
      </Typography>
      <SessionDetail data={data} />
      <Typography mt={4} mb={2} variant="h5">
        History
      </Typography>
      <SessionHistory id={id} />
      <Typography mt={4} mb={2} variant="h5">
        Debug Message
      </Typography>
      <DebugMessage message={data.debug_message} />
    </Fragment>
  );
};

export default Session;
