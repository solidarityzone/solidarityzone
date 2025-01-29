import { Button, Grid, Stack, Typography } from '@mui/material';

import { CourtsAutocomplete } from '~/components/CourtsAutocomplete';
import { RegionsAutocomplete } from '~/components/RegionsAutocomplete';
import { DateRangePicker } from '~/components/DateRangePicker';
import { FreeAutocomplete } from '~/components/FreeAutocomplete';

import type { FormEvent } from 'react';
import type { DateValue } from '~/types';

export type CasesFilterValues = {
  articles: string[];
  courts: number[];
  defendants: string[];
  judges: string[];
  regions: number[];
  entryDateFrom: DateValue;
  entryDateTo: DateValue;
  resultDateFrom: DateValue;
  resultDateTo: DateValue;
  effectiveDateFrom: DateValue;
  effectiveDateTo: DateValue;
};

type Props = {
  disabled: boolean;
  onChange: (values: CasesFilterValues) => void;
  onClear: () => void;
  onSubmit: () => void;
  values: CasesFilterValues;
};

export const CasesFilter = ({
  onSubmit,
  onChange,
  onClear,
  disabled,
  values,
}: Props) => {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  const handleChange = (name: string, value: string[] | number[]) => {
    onChange({
      ...values,
      [name]: value,
    });
  };

  const handleDateChange = (
    id: string,
    from: string | null,
    to: string | null,
  ) => {
    onChange({
      ...values,
      [`${id}From`]: from,
      [`${id}To`]: to,
    });
  };

  return (
    <form autoComplete="off" onSubmit={handleSubmit}>
      <Typography mb={1} variant="subtitle2" fontWeight="bold">
        Filter
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <FreeAutocomplete
            disabled={disabled}
            id="defendants"
            label="Defendants"
            onChange={handleChange}
            placeholder="Add name of defendant"
            value={values.defendants}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FreeAutocomplete
            disabled={disabled}
            id="judges"
            label="Judges"
            onChange={handleChange}
            placeholder="Add name of judge"
            value={values.judges}
          />
        </Grid>
        <Grid item xs={12}>
          <FreeAutocomplete
            disabled={disabled}
            id="articles"
            label="Articles"
            onChange={handleChange}
            placeholder="Add article"
            value={values.articles}
          />
        </Grid>
        <Grid item xs={12}>
          <CourtsAutocomplete
            disabled={disabled}
            id="courts"
            label="Courts"
            onChange={handleChange}
            placeholder="Search for a court"
            value={values.courts}
          />
        </Grid>
        <Grid item xs={12}>
          <RegionsAutocomplete
            disabled={disabled}
            id="regions"
            label="Regions"
            onChange={handleChange}
            placeholder="Search for a region"
            value={values.regions}
          />
        </Grid>
        <Grid item xs={6} md={4}>
          <Typography mb={2} variant="subtitle2" fontWeight="bold">
            Entry Date
          </Typography>
          <Stack spacing={2} direction="row">
            <DateRangePicker
              id="entryDate"
              from={values.entryDateFrom}
              to={values.entryDateTo}
              onChange={handleDateChange}
            />
          </Stack>
        </Grid>
        <Grid item xs={6} md={4}>
          <Typography mb={2} variant="subtitle2" fontWeight="bold">
            Result Date
          </Typography>
          <Stack spacing={2} direction="row">
            <DateRangePicker
              id="resultDate"
              from={values.resultDateFrom}
              to={values.resultDateTo}
              onChange={handleDateChange}
            />
          </Stack>
        </Grid>
        <Grid item xs={6} md={4}>
          <Typography mb={2} variant="subtitle2" fontWeight="bold">
            Effective Date
          </Typography>
          <Stack spacing={2} direction="row">
            <DateRangePicker
              id="effectiveDate"
              from={values.effectiveDateFrom}
              to={values.effectiveDateTo}
              onChange={handleDateChange}
            />
          </Stack>
        </Grid>
      </Grid>
      <Grid mt={0.1} container spacing={2}>
        <Grid item xs={12}>
          <Button variant="contained" type="submit" disabled={disabled}>
            Search
          </Button>
          <Button
            sx={{ ml: 1 }}
            variant="outlined"
            disabled={disabled}
            onClick={onClear}
          >
            Clear
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};
