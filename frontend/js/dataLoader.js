// fetchAPI: helper function to fetch JSON data from API endpoints
export async function fetchAPI(endpoint) {
  const res = await fetch(endpoint);
  if (!res.ok) throw new Error(`HTTP ${res.status} loading ${endpoint}`);
  return res.json();
}

// hide loading overlay after data is loaded and rendered
export function hideLoading() {
  const el = document.getElementById('loadingOverlay');
  el.classList.add('hidden');
  setTimeout(() => { el.style.display = 'none'; }, 500);
}