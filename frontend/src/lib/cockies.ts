import Cookies from 'js-cookie'

const TOKEN_COOKIE_KEY = 'token-portal-metarh'

export const setAuthToken = (token: string, expiresDays: number = 7) => {
  Cookies.set(TOKEN_COOKIE_KEY, token)
}

export const getAuthToken = () => {
  const token = Cookies.get(TOKEN_COOKIE_KEY)
  return token
}

export const removeAuthToken = () => {
  Cookies.remove(TOKEN_COOKIE_KEY)
}
