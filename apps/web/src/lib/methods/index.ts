import { methodCatalog } from "@/lib/methods/catalog";
import type { Method, MethodCategory } from "@/types/methods";

export const methodCategoryLabels: Record<MethodCategory, string> = {
  quantitative: "定量分析",
  configurational: "组态分析",
};

export function getMethodSlugs() {
  return methodCatalog.map((method) => method.slug);
}

export async function getMethods(): Promise<Method[]> {
  return [...methodCatalog];
}

export async function getFeaturedMethods(): Promise<Method[]> {
  const methods = await getMethods();
  return methods.filter((method) => method.isRecommended);
}

export function findMethodBySlug(slug: string): Method | null {
  return methodCatalog.find((method) => method.slug === slug) ?? null;
}

export async function getMethodBySlug(slug: string): Promise<Method | null> {
  return findMethodBySlug(slug);
}
