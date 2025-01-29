import { OutlinedInput } from '@mui/material';

type Props = {
  message: string;
};

export const DebugMessage = ({ message }: Props) => {
  return (
    <OutlinedInput
      fullWidth
      size="small"
      maxRows={10}
      multiline
      inputProps={{
        style: {
          fontSize: 10,
          background: 'black',
          color: 'white',
          fontFamily: 'monospace',
          lineHeight: 1,
        },
      }}
      readOnly
      defaultValue={message}
    />
  );
};
