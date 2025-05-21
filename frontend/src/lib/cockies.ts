import Cookies from "js-cookie";

const TOKEN_COOKIE_KEY = "token-portal-metarh";

export const setAuthToken = (token: string, expiresDays: number = 7) => {
  Cookies.set(TOKEN_COOKIE_KEY, token, {
    expires: expiresDays,
    secure: true,
    sameSite: "Lax",
  });
};

export const getAuthToken = (): string => {
  const token = Cookies.get(TOKEN_COOKIE_KEY);
  if (typeof token === "undefined") {
    return "";
  }
  return token;
};

export const removeAuthToken = () => {
  Cookies.remove(TOKEN_COOKIE_KEY);
};
