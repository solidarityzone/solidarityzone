import { AsyncAutocomplete } from './AsyncAutocomplete';

type Props = {
  disabled: boolean;
  id: string;
  label: string;
  onChange: (name: string, value: number[]) => void;
  placeholder: string;
  value: number[];
};

export const RegionsAutocomplete = ({
  disabled,
  id,
  label,
  onChange,
  placeholder,
  value,
}: Props) => {
  return (
    <AsyncAutocomplete
      disabled={disabled}
      id={id}
      label={label}
      onChange={onChange}
      path="/api/regions"
      placeholder={placeholder}
      value={value}
    />
  );
};
