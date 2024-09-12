import React from 'react';

export const Alert = ({ children, variant = 'default' }) => {
  const baseStyles = "p-4 mb-4 rounded-lg";
  const variantStyles = {
    default: "bg-blue-100 text-blue-800",
    destructive: "bg-red-100 text-red-800",
  };

  return (
    <div className={`${baseStyles} ${variantStyles[variant]}`}>
      {children}
    </div>
  );
};

export const AlertDescription = ({ children }) => {
  return <p className="text-sm">{children}</p>;
};