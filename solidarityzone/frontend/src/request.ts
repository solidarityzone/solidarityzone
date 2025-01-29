export async function get<O>(
  path: string,
  params?: URLSearchParams,
): Promise<O> {
  const url = params ? `${path}?${params}` : path;
  const response = await window.fetch(url, {
    method: 'GET',
  });
  return response.json();
}

export async function post<I, O>(path: string, body: I): Promise<O> {
  const response = await window.fetch(path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  return response.json();
}
