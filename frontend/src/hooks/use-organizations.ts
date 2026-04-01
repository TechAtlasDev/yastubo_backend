import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationsApi, Company, BusinessUnit } from "@/lib/api/organizations";

export const useCompanies = () => {
  return useQuery({
    queryKey: ["companies"],
    queryFn: organizationsApi.getCompanies,
  });
};

export const useCompany = (id: string) => {
  return useQuery({
    queryKey: ["company", id],
    queryFn: () => organizationsApi.getCompany(id),
    enabled: !!id,
  });
};

export const useCreateCompany = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (company: Partial<Company>) =>
      organizationsApi.createCompany(company),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["companies"] });
    },
  });
};

export const useBusinessUnits = (companyId: string) => {
  return useQuery({
    queryKey: ["business-units", companyId],
    queryFn: () => organizationsApi.getBusinessUnits(companyId),
    enabled: !!companyId,
  });
};

export const useCreateBusinessUnit = (companyId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (unit: Partial<BusinessUnit>) =>
      organizationsApi.createBusinessUnit(companyId, unit),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["business-units", companyId],
      });
    },
  });
};
