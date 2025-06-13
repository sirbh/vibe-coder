import { ProjectForm } from "@/components/custom/ProjectForm";

export default function Home() {
  return (
    <div className="relative flex items-center justify-center min-h-screen bg-gradient-to-br from-zinc-800 via-zinc-700 to-zinc-900 text-white py-[30px]">
      <ProjectForm />
    </div>
  );
}
