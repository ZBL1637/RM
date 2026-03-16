export function getApiBaseUrl() {
  const configuredUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.API_BASE_URL;

  if (configuredUrl) {
    return configuredUrl.replace(/\/$/, "");
  }

  if (process.env.NODE_ENV !== "production") {
    return "http://127.0.0.1:8000";
  }

  return "";
}
