"use client"

import { useEffect, useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from "../ui/card"
import axiosInstance from "@/lib/axios"
import { Loader2Icon } from "lucide-react"
import { useRouter } from "next/navigation"

const formSchema = z.object({
    projectName: z
        .string()
        .min(2, { message: "Project name must be at least 2 characters." })
        .regex(/^[A-Za-z]+$/, {
            message: "Project name must contain only alphabets with no spaces or special characters.",
        }),
})

type Project = {
    project_name: string
    container_name: string
    port: number
}

export function ProjectForm() {
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            projectName: "",
        },
    })

    const [projects, setProjects] = useState<Project[]>([])
    const router = useRouter()

    // Load existing projects on mount
    useEffect(() => {
        const existing = JSON.parse(localStorage.getItem("projects") || "[]")
        setProjects(existing)
    }, [])

    async function onSubmit(values: z.infer<typeof formSchema>) {
        try {
            const response = await axiosInstance.get("/create-project/", {
                params: {
                    project_name: values.projectName,
                },
            })

            if (response.status === 201 && response.data?.status === "success") {
                const newProject: Project = {
                    container_name: response.data.container_name,
                    port: response.data.port,
                    project_name: values.projectName,
                }

                const updatedProjects = [...projects, newProject]
                localStorage.setItem("projects", JSON.stringify(updatedProjects))

                router.push(`/project?container_name=${newProject.container_name}&project_name=${newProject.project_name}&port=${newProject.port}`)
            } else {
                console.error("Failed to create project:", response.data)
                form.setError("projectName", {
                    type: "manual",
                    message: "Failed to create project. Please try again.",
                })
            }
        } catch (error) {
            console.error("Error creating project:", error)
            form.setError("projectName", {
                type: "manual",
                message: "An error occurred while creating the project. Please try again.",
            })
        }
    }

    return (
        <div className="max-w-xl mx-auto mt-10 space-y-6">
            <Card className="bg-white shadow-lg rounded-lg p-6">
                <CardHeader>
                    <CardTitle>
                        <h1 className="text-2xl font-bold text-center">Create Project</h1>
                    </CardTitle>
                    <CardDescription>
                        Ready to bring your idea to life? Just enter the project details below and kickstart your next big thing!
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                            <FormField
                                control={form.control}
                                name="projectName"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Project Name</FormLabel>
                                        <FormControl>
                                            <Input placeholder="project name" {...field} />
                                        </FormControl>
                                        <FormDescription>
                                            Enter a project name that is at least 2 characters long and contains only alphabets.
                                        </FormDescription>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <Button type="submit" disabled={form.formState.isSubmitting} className="w-full">
                                {form.formState.isSubmitting ? (
                                    <Loader2Icon className="animate-spin mr-2" />
                                ) : null}
                                {form.formState.isSubmitting ? "Creating Project..." : "Create Project"}
                            </Button>
                        </form>
                    </Form>
                </CardContent>
            </Card>

            {projects.length > 0 && (
                <Card className="bg-white shadow-md rounded-lg p-4">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold">Previous Projects</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2">
                            {projects.map((proj, idx) => (
                                <li key={idx}>
                                    <button
                                        className="text-blue-600 underline hover:text-blue-800"
                                        onClick={() =>
                                            router.push(`/project?container_name=${proj.container_name}&project_name=${proj.project_name}&port=${proj.port}`)
                                        }
                                    >
                                        🚀 {proj.project_name} 
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}
