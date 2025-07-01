import React from "react";

const LoadingSpinner = ({ size = "md", className = "" }) => {
  const sizes = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };

  return (
    <div
      className={`animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 ${sizes[size]} ${className}`}
    />
  );
};

const LoadingPage = ({ message = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-64 py-12">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
};

const LoadingButton = ({ size = "sm" }) => {
  return <LoadingSpinner size={size} className="text-current" />;
};

export { LoadingSpinner, LoadingPage, LoadingButton };
export default LoadingSpinner;
