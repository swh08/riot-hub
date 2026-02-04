import axios from "axios";

export const http = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 15000,
});

http.interceptors.response.use(
  (res) => res,
  (error) => {
    return Promise.reject(error);
  },
);
