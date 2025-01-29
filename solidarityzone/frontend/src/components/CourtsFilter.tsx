import { Button, Grid, Typography } from '@mui/material';

import { RegionsAutocomplete } from '~/components/RegionsAutocomplete';

import type { FormEvent } from 'react';

export type CourtsFilterValue = {
  regions: number[];
};

type Props = {
  disabled: boolean;
  onChange: (values: CourtsFilterValue) => void;
  onClear: () => void;
  onSubmit: () => void;
  values: CourtsFilterValue;
};

export const CourtsFilter = ({
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

  return (
    <form autoComplete="off" onSubmit={handleSubmit}>
      <Typography mb={1} variant="subtitle2" fontWeight="bold">
        Filter
      </Typography>
      <Grid container spacing={2}>
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
