import axios from "axios";

const baseURL = "/api";

export const http = axios.create({
  baseURL,
  timeout: 15000,
});

http.interceptors.response.use(
  (res) => res,
  (error) => {
    return Promise.reject(error);
  },
);
