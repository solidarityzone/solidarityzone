import { Container } from '@mui/material';

type Props = {
  children: React.ReactNode;
};

const Main = ({ children }: Props) => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {children}
    </Container>
  );
};

export default Main;
