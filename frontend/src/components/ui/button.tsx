import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-full text-sm font-medium transition disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary px-5 py-3 text-primary-foreground hover:opacity-90",
        secondary: "bg-muted px-5 py-3 text-foreground hover:bg-accent",
        ghost: "px-4 py-2 text-foreground hover:bg-muted",
        outline: "border border-border bg-white px-5 py-3 hover:bg-muted"
      }
    },
    defaultVariants: { variant: "default" }
  }
);

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, ...props }, ref) => (
  <button className={cn(buttonVariants({ variant }), className)} ref={ref} {...props} />
));

Button.displayName = "Button";
