import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => (
  <input className={cn("flex h-11 w-full rounded-2xl border border-border bg-input px-4 py-2 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none", className)} ref={ref} {...props} />
));

Input.displayName = "Input";
