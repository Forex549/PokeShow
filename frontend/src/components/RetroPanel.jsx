/**
 * RetroPanel — thick-border "window" panel, Showdown-2004 aesthetic.
 * Props:
 *   className  — extra Tailwind classes
 *   inset      — use arena/inset variant instead of standard panel
 *   children
 */
function RetroPanel({ children, className = "", inset = false }) {
  return (
    <div className={`${inset ? "retro-panel-inset" : "retro-panel"} ${className}`}>
      {children}
    </div>
  );
}

export default RetroPanel;
