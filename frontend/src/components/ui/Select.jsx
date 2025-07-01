import React from "react";

const Select = ({
  label,
  error,
  options = [],
  value,
  onChange,
  disabled = false,
  required = false,
  placeholder = "Select an option",
  className = "",
  ...props
}) => {
  const selectClasses = `block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 ${
    error ? "ring-red-300 focus:ring-red-600" : ""
  } ${disabled ? "bg-gray-50 text-gray-500" : ""} ${className}`;

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium leading-6 text-gray-900 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <select
        className={selectClasses}
        value={value}
        onChange={onChange}
        disabled={disabled}
        required={required}
        {...props}
      >
        <option value="">{placeholder}</option>
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
};

export default Select;
