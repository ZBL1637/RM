import { notFound } from "next/navigation";

import { MethodsPageContent } from "@/components/methods-page-content";
import { getMethods } from "@/lib/methods";
import type { MethodCategory } from "@/types/methods";

type MethodCategoryPageProps = {
  params: Promise<{
    category: string;
  }>;
};

const categories: MethodCategory[] = ["quantitative", "configurational"];

export function generateStaticParams() {
  return categories.map((category) => ({ category }));
}

export const dynamicParams = false;

export default async function MethodCategoryPage({ params }: MethodCategoryPageProps) {
  const { category } = await params;

  if (!categories.includes(category as MethodCategory)) {
    notFound();
  }

  const methods = await getMethods();

  return <MethodsPageContent methods={methods} selectedCategory={category as MethodCategory} />;
}
