import { Close } from '@mui/icons-material';
import { Dialog, DialogContent, DialogTitle, IconButton } from '@mui/material';

import { CaseDetail } from '~/components/CaseDetail';

import type { Case } from '~/types';

type Props = {
  selected?: Case;
  handleClose: () => void;
};

export const CaseDetailDialog = ({ selected, handleClose }: Props) => {
  return (
    <Dialog onClose={handleClose} open={selected !== undefined}>
      <DialogTitle>
        {selected?.case_number}
        <IconButton
          onClick={handleClose}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        {selected && <CaseDetail data={selected} />}
      </DialogContent>
    </Dialog>
  );
};
