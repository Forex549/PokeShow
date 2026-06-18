function Logo({ className = "", width = 260, height = "auto", alt = "PokeShow" }) {
  return (
    <img
      src="/backgrounds/poke_fondo.png"
      alt={alt}
      className={className}
      style={{ width, height, objectFit: "contain", display: "block", margin: "0 auto" }}
    />
  );
}

export default Logo;
