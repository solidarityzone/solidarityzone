import { Routes, Route } from 'react-router-dom';

import Case from '~/views/Case';
import Cases from '~/views/Cases';
import Court from '~/views/Court';
import Courts from '~/views/Courts';
import Session from '~/views/Session';
import Sessions from '~/views/Sessions';

const Router = () => {
  return (
    <Routes>
      <Route path="/" element={<Cases />} />
      <Route path="/cases/:id" element={<Case />} />
      <Route path="/courts" element={<Courts />} />
      <Route path="/courts/:id" element={<Court />} />
      <Route path="/sessions" element={<Sessions />} />
      <Route path="/sessions/:id" element={<Session />} />
    </Routes>
  );
};

export default Router;
