import { Close } from '@mui/icons-material';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
} from '@mui/material';

import { formatDateTime } from '~/utils';
import { SessionDetail } from '~/components/SessionDetail';
import { DebugMessage } from '~/components/DebugMessage';

import type { ScrapeSession } from '~/types';

type Props = {
  session?: ScrapeSession;
  handleClose: () => void;
};

export const SessionDetailDialog = ({ session, handleClose }: Props) => (
  <Dialog onClose={handleClose} open={session !== undefined}>
    <DialogTitle>
      Session {formatDateTime(session?.created_at)}
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
      {session && <SessionDetail data={session} />}
      <Typography mt={2} variant="subtitle1" fontWeight="bold">
        Debug Message
      </Typography>
      {session && <DebugMessage message={session.debug_message} />}
    </DialogContent>
  </Dialog>
);
