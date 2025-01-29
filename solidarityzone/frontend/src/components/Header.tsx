import { AppBar, Box, Toolbar, Typography, Link, Avatar } from '@mui/material';
import { NavLink } from 'react-router-dom';

import { NavButton } from '~/components/NavButton';

const Header = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Link component={NavLink} to="/">
          <Box display="flex">
            <Avatar src="/static/assets/favicon.png" />
            <Typography
              ml={2}
              lineHeight={2}
              variant="h6"
              color="white"
              fontWeight="bold"
              component="div"
            >
              Solidarity Zone
            </Typography>
          </Box>
        </Link>
        <Box ml={'auto'} display="flex">
          <NavButton to="/" label="Search" />
          <NavButton to="/courts" label="Courts" />
          <NavButton to="/sessions" label="Scraper" />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
