import { AccountBalance } from '@mui/icons-material';
import { Button, Link, Typography } from '@mui/material';
import { Fragment, useEffect, useState } from 'react';
import { NavLink, useParams } from 'react-router-dom';

import { CourtHistory } from '~/components/CourtHistory';
import { get } from '~/request';

import type { Court as CourtType } from '~/types';

const Court = () => {
  const [data, setData] = useState<CourtType | undefined>();
  const { id } = useParams();

  useEffect(() => {
    const fetchData = async () => {
      if (!id) {
        return;
      }

      const response = await get<CourtType>(`/api/courts/${id}`);
      setData(response);
    };

    fetchData();
  }, [id]);

  return !data || !id ? (
    <p>'Loading ...'</p>
  ) : (
    <Fragment>
      <Typography mb={2} variant="h5">
        <AccountBalance /> {data.name} ({data.region.name})
      </Typography>
      <Link component={NavLink} to={`/?court=${data.id}`}>
        <Button variant="contained">Show all cases</Button>
      </Link>
      <Typography mt={4} mb={2} variant="h5">
        History
      </Typography>
      <CourtHistory id={id} />
    </Fragment>
  );
};

export default Court;
