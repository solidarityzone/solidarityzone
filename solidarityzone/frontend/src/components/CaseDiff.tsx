import { useMemo } from 'react';

import { CaseDetail } from '~/components/CaseDetail';

import type { Case } from '~/types';

type Diff = {
  [name: string]: string | null;
};

type Props = {
  diff: string;
};

export const CaseDiff = ({ diff }: Props) => {
  const data: Diff = useMemo(() => {
    return JSON.parse(diff);
  }, [diff]);

  return <CaseDetail data={data as unknown as Partial<Case>} />;
};
