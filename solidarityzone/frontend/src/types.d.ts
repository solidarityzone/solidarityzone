export type PaginationInfo = {
  itemsPerPage: number;
  totalItems: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  startCursor: string;
  endCursor: string;
};

export type PaginationResult<T> = {
  pagination: PaginationInfo;
  items: T[];
};

export type PaginationArgs = {
  itemsPerPage?: number;
  before?: string;
  after?: string;
};

export type Base = {
  id: number;
  created_at: string;
  updated_at: string;
};

export type Court = Base & {
  name: string;
  code: string;
  region: Region;
};

export type Region = Base & {
  name: string;
};

export type ScrapeSession = Base & {
  created_cases: number;
  updated_cases: number;
  input_article: string;
  input_court_code: string;
  is_successful: boolean;
  is_captcha: boolean;
  is_captcha_successful: boolean;
  error_type: string;
  ignored_cases: number;
  court: Court;
  region: Region;
  debug_message: string;
};

export type ScrapeLog = Base & {
  diff: string;
  is_update: boolean;
  case: Case;
  scrape_session_id: number;
};

export type Case = Base & {
  articles: string;
  case_number: string;
  defendant_name: string;
  judge_name: string;
  entry_date: string;
  effective_date: string;
  result_date: string;
  result: string;
  sub_type: string;
  url: string;
  court: Court;
  region: Region;
};

export type DateValue = string | null;
