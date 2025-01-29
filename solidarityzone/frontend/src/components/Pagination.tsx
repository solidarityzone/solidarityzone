import { KeyboardArrowLeft, KeyboardArrowRight } from '@mui/icons-material';
import {
  IconButton,
  MenuItem,
  Select,
  SelectChangeEvent,
  Toolbar,
  Typography,
} from '@mui/material';

export type PaginationProps = {
  totalItems?: number;
  rowsPerPageOptions: number[];
  rowsPerPage?: number;
  onNextPage: () => void;
  onPreviousPage: () => void;
  onRowsPerPageChange: (event: SelectChangeEvent<number>) => void;
  hasNextPage?: boolean;
  hasPreviousPage?: boolean;
};

export const Pagination = ({
  totalItems,
  onRowsPerPageChange,
  rowsPerPageOptions,
  rowsPerPage,
  hasNextPage = false,
  hasPreviousPage = false,
  onNextPage,
  onPreviousPage,
}: PaginationProps) => {
  return (
    <Toolbar
      variant="dense"
      sx={{
        borderBottom: '1px solid rgba(224, 224, 224, 1)',
      }}
    >
      <div style={{ flex: '1 1 100%' }} />
      <Typography variant="body2" flexShrink={0} mr={2}>
        Rows per page:
      </Typography>
      <Select
        variant="standard"
        size="small"
        style={{ fontSize: '0.875rem' }}
        value={rowsPerPage}
        onChange={onRowsPerPageChange}
      >
        {rowsPerPageOptions.map((rowsPerPageOption) => (
          <MenuItem
            key={rowsPerPageOption}
            style={{ fontSize: '0.875rem' }}
            value={rowsPerPageOption}
          >
            {rowsPerPageOption}
          </MenuItem>
        ))}
      </Select>
      <Typography variant="body2" flexShrink={0} ml={3} mr={3}>
        {`${totalItems}`} total
      </Typography>
      <IconButton
        aria-label="previous"
        disabled={!hasPreviousPage}
        size="small"
        onClick={onPreviousPage}
      >
        <KeyboardArrowLeft />
      </IconButton>
      <IconButton
        aria-label="next"
        disabled={!hasNextPage}
        size="small"
        onClick={onNextPage}
      >
        <KeyboardArrowRight />
      </IconButton>
    </Toolbar>
  );
};
