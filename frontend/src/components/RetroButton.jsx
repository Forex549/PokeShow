/**
 * RetroButton — pixel-bordered button, Showdown-2004 aesthetic.
 * Props:
 *   variant   — "primary" | "secondary" | "neutral" | "danger"  (default: "primary")
 *   size      — "sm" | "md" | "lg"  (default: "md")
 *   disabled  — bool
 *   onClick   — handler
 *   className — extra classes
 *   children
 */
function RetroButton({
  children,
  variant = "primary",
  size = "md",
  disabled = false,
  onClick,
  className = "",
  type = "button",
}) {
  const variantClass = {
    primary:   "retro-btn-primary",
    secondary: "retro-btn-secondary",
    neutral:   "retro-btn-neutral",
    danger:    "retro-btn-danger",
  }[variant] ?? "retro-btn-primary";

  const sizeClass = {
    sm: "text-[0.45rem] px-3 py-2",
    md: "text-[0.55rem] px-5 py-3",
    lg: "text-[0.65rem] px-7 py-4",
  }[size] ?? "text-[0.55rem] px-5 py-3";

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`retro-btn ${variantClass} ${sizeClass} ${className}`}
    >
      {children}
    </button>
  );
}

export default RetroButton;
