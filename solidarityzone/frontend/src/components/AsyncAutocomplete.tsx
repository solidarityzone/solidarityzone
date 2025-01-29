import { Autocomplete, TextField } from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { debounce } from '@mui/material/utils';

import { useResolveIdQuery } from '~/hooks';

import type { PaginationResult } from '~/types';

interface WithNameAndId {
  name: string;
  id: number;
}

type Props = {
  path: string;
  disabled: boolean;
  id: string;
  label: string;
  onChange: (name: string, value: number[]) => void;
  placeholder: string;
  value: number[];
};

async function request<T extends WithNameAndId>(
  path: string,
  name: string,
): Promise<T[]> {
  const response = await window.fetch(`${path}?name=${name}`);
  const result: PaginationResult<T> = await response.json();
  return result.items;
}

export function AsyncAutocomplete<T extends WithNameAndId>({
  path,
  disabled,
  id,
  label,
  onChange,
  placeholder,
  value,
}: Props) {
  const [resolved, isResolverLoading] = useResolveIdQuery<T>(path, value);
  const [options, setOptions] = useState<readonly T[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fetch = useMemo(
    () =>
      debounce(
        (input: { name: string }, callback: (results?: readonly T[]) => void) =>
          request<T>(path, input.name).then(callback),
        400,
      ),
    [path],
  );

  useEffect(() => {
    let active = true;

    if (inputValue === '') {
      setOptions(resolved);
      return;
    }

    setIsLoading(true);

    fetch({ name: inputValue }, (results?: readonly T[]) => {
      if (active) {
        let newOptions: readonly T[] = resolved;

        if (results) {
          newOptions = [...newOptions, ...results];
        }

        setOptions(newOptions);
        setIsLoading(false);
      }
    });

    return () => {
      active = false;
    };
  }, [fetch, resolved, inputValue]);

  return (
    <Autocomplete
      id={id}
      multiple
      defaultValue={[]}
      options={options}
      value={resolved}
      disabled={disabled || isResolverLoading}
      loading={isLoading}
      getOptionLabel={(option) => option.name}
      filterSelectedOptions
      isOptionEqualToValue={(option, value) => option.id === value.id}
      onInputChange={(_, newInputValue) => {
        setInputValue(newInputValue);
      }}
      onChange={(_event: React.SyntheticEvent, newValue: T[]) => {
        if (newValue) {
          onChange(
            id,
            newValue.map((value) => value.id),
          );
        } else {
          onChange(id, []);
        }
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          variant="outlined"
          label={label}
          placeholder={placeholder}
        />
      )}
      renderOption={(props, option, index) => {
        const key = `item-${index}-${option.id}`;
        return (
          <li {...props} key={key}>
            {option.name}
          </li>
        );
      }}
    />
  );
}
