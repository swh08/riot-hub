import axios from "axios";

export const http = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 15000,
});

// 可选：统一处理错误/日志
http.interceptors.response.use(
  (res) => res,
  (error) => {
    return Promise.reject(error);
  },
);
