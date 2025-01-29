import { Typography } from '@mui/material';

type Props = {
  version: string;
};

const Footer = ({ version }: Props) => {
  return (
    <Typography
      textAlign={'center'}
      mt={1}
      mb={2}
      variant="subtitle2"
      color="inherit"
      component="div"
    >
      v{version}
    </Typography>
  );
};

export default Footer;
