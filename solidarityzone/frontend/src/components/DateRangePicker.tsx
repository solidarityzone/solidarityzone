import { DatePicker } from '@mui/x-date-pickers';
import { DateTime } from 'luxon';
import { Fragment, useMemo } from 'react';

import { DATE_FORMAT } from '~/constants';

import type { DateValue } from '~/types';

type Props = {
  id: string;
  onChange: (id: string, from: DateValue, to: DateValue) => void;
  from: DateValue;
  to: DateValue;
};

export const DateRangePicker = ({ id, from, to, onChange }: Props) => {
  const handleChange = (name: 'from' | 'to', value: DateValue) => {
    if (name === 'from') {
      onChange(id, value, to);
    } else if (name === 'to') {
      onChange(id, from, value);
    }
  };

  const luxonFrom = useMemo(() => {
    if (from) {
      return DateTime.fromISO(from);
    } else {
      return null;
    }
  }, [from]);

  const luxonTo = useMemo(() => {
    if (to) {
      return DateTime.fromISO(to);
    } else {
      return null;
    }
  }, [to]);

  return (
    <Fragment>
      <DatePicker
        label="From"
        value={luxonFrom}
        format={DATE_FORMAT}
        maxDate={luxonTo ? luxonTo : undefined}
        onChange={(newValue: DateTime | null) => {
          handleChange('from', newValue ? newValue.toISODate() : null);
        }}
      />
      <DatePicker
        label="To"
        value={luxonTo}
        minDate={luxonFrom ? luxonFrom : undefined}
        format={DATE_FORMAT}
        onChange={(newValue: DateTime | null) => {
          handleChange('to', newValue ? newValue.toISODate() : null);
        }}
      />
    </Fragment>
  );
};
