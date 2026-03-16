import { MethodsPageContent } from "@/components/methods-page-content";
import { getMethods } from "@/lib/methods";

export default async function MethodsPage() {
  const methods = await getMethods();

  return <MethodsPageContent methods={methods} selectedCategory="all" />;
}
