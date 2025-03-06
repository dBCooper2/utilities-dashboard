import * as React from "react";

interface HeadingProps extends React.HTMLAttributes<HTMLHeadingElement> {
  size?: "sm" | "md" | "lg" | "xl";
}

export function Heading({ size = "md", className, ...props }: HeadingProps) {
  const baseStyle = "font-bold text-gray-900";
  const sizeStyles = {
    sm: "text-sm",
    md: "text-lg",
    lg: "text-2xl",
    xl: "text-3xl",
  };

  return (
    <h1
      className={`${baseStyle} ${sizeStyles[size]} ${className || ""}`}
      {...props}
    />
  );
} 