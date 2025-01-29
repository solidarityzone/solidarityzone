import {
  AccountBalance,
  Alarm,
  Announcement,
  Article,
  ChangeCircle,
  Gavel,
  LocationCity,
  NewReleases,
  NoteAdd,
  Person,
  Link as LinkIcon,
} from '@mui/icons-material';
import { Chip, Stack } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

import { formatDate, formatDateTime } from '~/utils';

import type { Case } from '~/types';

type Props = {
  data: Partial<Case>;
};

export const CaseDetail = ({ data }: Props) => {
  return (
    <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
      {'defendant_name' in data && (
        <Chip
          icon={<Person />}
          color="primary"
          component={RouterLink}
          to={`/?defendant=${data.defendant_name}`}
          clickable
          label={
            <span>
              <strong>Defendant</strong>: {data.defendant_name}
            </span>
          }
        />
      )}
      {data.judge_name && (
        <Chip
          icon={<Person />}
          color="primary"
          component={RouterLink}
          to={`/?judge=${data.judge_name}`}
          clickable
          label={
            <span>
              <strong>Judge</strong>: {data.judge_name}
            </span>
          }
        />
      )}
      {data.case_number && (
        <Chip
          icon={<Article />}
          color="primary"
          label={
            <span>
              <strong>Case #</strong>: {data.case_number}
            </span>
          }
        />
      )}
      {data.articles && (
        <Chip
          icon={<Gavel />}
          color="primary"
          component={RouterLink}
          to={`/?article=${data.articles}`}
          clickable
          label={
            <span>
              <strong>Articles</strong>: {data.articles}
            </span>
          }
        />
      )}
      {data.sub_type && (
        <Chip
          icon={<AccountBalance />}
          color="info"
          label={
            <span>
              <strong>Subtype</strong>: {data.sub_type}
            </span>
          }
        />
      )}
      {data.court && 'name' in data.court && (
        <Chip
          icon={<AccountBalance />}
          color="info"
          component={RouterLink}
          to={`/courts/${data.court.id}`}
          clickable
          label={
            <span>
              <strong>Court</strong>: {data.court.name}
            </span>
          }
        />
      )}
      {data.court && 'code' in data.court && (
        <Chip
          icon={<AccountBalance />}
          color="info"
          label={
            <span>
              <strong>Court Code</strong>: <code>{data.court.code}</code>
            </span>
          }
        />
      )}
      {data.region && 'name' in data.region && (
        <Chip
          icon={<LocationCity />}
          color="info"
          component={RouterLink}
          to={`/courts?region=${data.region.id}`}
          clickable
          label={
            <span>
              <strong>Region</strong>: {data.region.name}
            </span>
          }
        />
      )}
      {'entry_date' in data && (
        <Chip
          icon={<Alarm />}
          color="secondary"
          label={
            <span>
              <strong>Entry Date</strong>: {formatDate(data.entry_date)}
            </span>
          }
        />
      )}
      {'result_date' in data && (
        <Chip
          icon={<Announcement />}
          color="secondary"
          label={
            <span>
              <strong>Result</strong>: {data.result ? data.result : 'n.a'}
              {` (${formatDate(data.result_date)})`}
            </span>
          }
        />
      )}
      {'effective_date' in data && (
        <Chip
          icon={<NewReleases />}
          color="secondary"
          label={
            <span>
              <strong>Effective Date</strong>:{' '}
              {data.effective_date ? formatDate(data.effective_date) : 'n.a'}
            </span>
          }
        />
      )}
      {'created_at' in data && (
        <Chip
          icon={<NoteAdd />}
          variant="outlined"
          label={
            <span>
              <strong>Created At</strong>: {formatDateTime(data.created_at)}
            </span>
          }
        />
      )}
      {'updated_at' in data && (
        <Chip
          icon={<ChangeCircle />}
          variant="outlined"
          label={
            <span>
              <strong>Last Updated At</strong>:{' '}
              {formatDateTime(data.updated_at)}
            </span>
          }
        />
      )}
      {data.url && (
        <Chip
          component="a"
          icon={<LinkIcon />}
          href={data.url}
          target="_blank"
          clickable
          variant="outlined"
          title={data.url}
          label={
            <span>
              <strong>URL</strong>: {`${data.url.slice(0, 100)} ...`}
            </span>
          }
        />
      )}
    </Stack>
  );
};
