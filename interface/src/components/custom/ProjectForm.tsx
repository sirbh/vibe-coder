"use client"

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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"

const formSchema = z.object({
  projectName: z
    .string()
    .min(2, { message: "Project name must be at least 2 characters." })
    .regex(/^[A-Za-z]+$/, {
      message: "Project name must contain only alphabets with no spaces or special characters.",
    }),
})

export function ProjectForm() {
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            projectName: "",
        },
    })

    // 2. Define a submit handler.
    function onSubmit(values: z.infer<typeof formSchema>) {
        // Do something with the form values.
        // ✅ This will be type-safe and validated.
        console.log(values)
    }

    return (
        <Card className="w-md h-md mx-auto mt-10 bg-white shadow-lg rounded-lg p-6">
            <CardHeader>
                <CardTitle>
                    <h1 className="text-2xl font-bold text-center">Create Project</h1>
                </CardTitle>
                <CardDescription>Ready to bring your idea to life? Just enter the project details below and kickstart your next big thing!</CardDescription>
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
                        <Button type="submit" className="w-full">Submit</Button>
                    </form>
                </Form>
            </CardContent>
        </Card>
    )
}