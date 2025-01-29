import { DateTime } from 'luxon';

import { ITEMS_PER_PAGE } from './constants';
import { PaginationArgs } from './types';

export function toPaginationParams(args: PaginationArgs): URLSearchParams {
  const params: {
    itemsPerPage?: string;
    before?: string;
    after?: string;
  } = {
    itemsPerPage: numberToParam(args.itemsPerPage, ITEMS_PER_PAGE),
  };

  if (args.before) {
    params.before = args.before;
  }

  if (args.after) {
    params.after = args.after;
  }

  return new URLSearchParams({ ...params });
}

export function paramToNumber(
  params: URLSearchParams,
  name: string,
  defaultValue: number,
): number {
  const param = params.get(name);
  return param ? parseInt(param) : defaultValue;
}

export function numberToParam(
  value: number | undefined,
  defaultValue: number,
): string {
  if (value) {
    return value.toString();
  } else {
    return defaultValue.toString();
  }
}

export function formatDate(dateString?: string): string {
  if (dateString) {
    return DateTime.fromISO(dateString).toFormat('dd.LL.yyyy');
  } else {
    return 'n.a.';
  }
}

export function formatDateTime(dateString?: string): string {
  if (dateString) {
    return DateTime.fromISO(dateString).toFormat('dd.LL.yyyy HH:mm');
  } else {
    return 'n.a.';
  }
}
