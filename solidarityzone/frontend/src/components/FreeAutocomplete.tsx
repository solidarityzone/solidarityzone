import { Autocomplete, TextField } from '@mui/material';

type Props = {
  disabled: boolean;
  id: string;
  label: string;
  onChange: (name: string, value: string[]) => void;
  placeholder: string;
  value: string[];
};

export const FreeAutocomplete = ({
  disabled,
  id,
  label,
  onChange,
  placeholder,
  value,
}: Props) => {
  return (
    <Autocomplete
      multiple
      id={id}
      options={[]}
      disabled={disabled}
      autoSelect
      value={value}
      defaultValue={value}
      freeSolo
      onChange={(_, values) => {
        onChange(id, values);
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          variant="outlined"
          label={label}
          placeholder={placeholder}
        />
      )}
    />
  );
};
