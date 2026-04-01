import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/store/auth.store";
import { useEffect } from "react";

export const useMe = () => {
  const { token, setAuth, logout } = useAuthStore();

  const query = useQuery({
    queryKey: ["me"],
    queryFn: authApi.getMe,
    enabled: !!token,
    retry: false,
  });

  useEffect(() => {
    if (query.data) {
      setAuth(token!, query.data);
    }
    if (query.isError) {
      logout();
    }
  }, [query.data, query.isError, token, setAuth, logout]);

  return query;
};
