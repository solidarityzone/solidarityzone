import CssBaseline from '@mui/material/CssBaseline';
import GlobalStyles from '@mui/material/GlobalStyles';
import { Fragment } from 'react';
import { HashRouter } from 'react-router-dom';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { green, orange } from '@mui/material/colors';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterLuxon } from '@mui/x-date-pickers/AdapterLuxon';

import Header from '~/components/Header';
import Footer from '~/components/Footer';
import Main from '~/components/Main';
import Router from '~/Router';

type Props = {
  version: string;
};

const theme = createTheme({
  palette: {
    primary: {
      main: '#82777d',
    },
    secondary: {
      main: orange[300],
    },
    info: {
      main: green[100],
    },
  },
});

const App = ({ version }: Props) => {
  return (
    <Fragment>
      <ThemeProvider theme={theme}>
        <LocalizationProvider dateAdapter={AdapterLuxon}>
          <CssBaseline />
          <GlobalStyles
            styles={{
              body: { backgroundColor: '#efefef' },
            }}
          />
          <HashRouter>
            <Header />
            <Main>
              <Router />
            </Main>
            <Footer version={version} />
          </HashRouter>
        </LocalizationProvider>
      </ThemeProvider>
    </Fragment>
  );
};

export default App;
