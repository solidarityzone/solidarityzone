import { Article } from '@mui/icons-material';
import { Typography } from '@mui/material';
import { Fragment, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import { CaseDetail } from '~/components/CaseDetail';
import { CaseHistory } from '~/components/CaseHistory';
import { get } from '~/request';

import type { Case as CaseType } from '~/types';

const Case = () => {
  const [data, setData] = useState<CaseType | undefined>();
  const { id } = useParams();

  useEffect(() => {
    const fetchData = async () => {
      if (!id) {
        return;
      }

      const response = await get<CaseType>(`/api/cases/${id}`);
      setData(response);
    };

    fetchData();
  }, [id]);

  return !data || !id ? (
    <Typography>Loading ...</Typography>
  ) : (
    <Fragment>
      <Typography mb={2} variant="h5">
        <Article /> {data.defendant_name} ({data.court.name})
      </Typography>
      <CaseDetail data={data} />
      <Typography mt={4} mb={2} variant="h5">
        History
      </Typography>
      <CaseHistory id={id} />
    </Fragment>
  );
};

export default Case;
