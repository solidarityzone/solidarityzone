import {
  AccountBalance,
  Add,
  ChangeCircle,
  Gavel,
  Nightlight,
  NoteAdd,
  RadioButtonChecked,
  Refresh,
} from '@mui/icons-material';
import { Chip, Stack } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

import { formatDateTime } from '~/utils';

import type { ScrapeSession } from '~/types';

type Props = {
  data: ScrapeSession;
};

export const SessionDetail = ({ data }: Props) => (
  <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
    <Chip
      icon={<Gavel />}
      color="primary"
      label={
        <span>
          <strong>Article</strong>: {data.input_article}
        </span>
      }
    />
    {data.court ? (
      <Chip
        icon={<AccountBalance />}
        color="primary"
        component={RouterLink}
        to={`/courts/${data.court.id}`}
        clickable
        label={
          <span>
            <strong>Court</strong>: {data.court.name}
          </span>
        }
      />
    ) : (
      <Chip
        icon={<AccountBalance />}
        color="primary"
        label={
          <span>
            <strong>Court</strong>: {data.input_court_code}
          </span>
        }
      />
    )}
    <Chip
      icon={<Add />}
      variant={data.created_cases ? 'filled' : 'outlined'}
      color={data.created_cases ? 'secondary' : 'primary'}
      label={
        <span>
          <strong>Created Cases</strong>: {data.created_cases}
        </span>
      }
    />
    <Chip
      icon={<Refresh />}
      variant={data.updated_cases ? 'filled' : 'outlined'}
      color={data.updated_cases ? 'info' : 'primary'}
      label={
        <span>
          <strong>Updated Cases</strong>: {data.updated_cases}
        </span>
      }
    />
    <Chip
      icon={<Nightlight />}
      variant="outlined"
      color={data.ignored_cases ? 'default' : 'primary'}
      label={
        <span>
          <strong>Ignored Cases</strong>: {data.ignored_cases}
        </span>
      }
    />
    <Chip
      icon={<RadioButtonChecked />}
      color={data.is_successful ? 'success' : 'error'}
      label={data.is_successful ? 'Completed' : data.error_type}
    />
    <Chip
      icon={<RadioButtonChecked />}
      color={
        data.is_captcha
          ? data.is_captcha_successful
            ? 'success'
            : 'error'
          : 'primary'
      }
      label={
        data.is_captcha
          ? data.is_captcha_successful
            ? 'Captcha challenge solved'
            : 'Captcha challenge failed'
          : 'No captcha required'
      }
    />
    <Chip
      icon={<NoteAdd />}
      variant="outlined"
      label={
        <span>
          <strong>Created At</strong>: {formatDateTime(data.created_at)}
        </span>
      }
    />
    <Chip
      icon={<ChangeCircle />}
      variant="outlined"
      label={
        <span>
          <strong>Last Updated At</strong>: {formatDateTime(data.updated_at)}
        </span>
      }
    />
  </Stack>
);
