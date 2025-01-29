import { Button, Link } from '@mui/material';
import { NavLink, useLocation } from 'react-router-dom';

type Props = {
  label: string;
  to: string;
};

export const NavButton = ({ to, label }: Props) => {
  const { pathname } = useLocation();

  return (
    <Link component={NavLink} to={to}>
      <Button
        sx={{
          my: 2,
          color: 'white',
          display: 'block',
          fontWeight: 'bold',
          borderRadius: 0,
          borderBottom: pathname == to ? '2px solid white' : null,
        }}
      >
        {label}
      </Button>
    </Link>
  );
};
