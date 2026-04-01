export const designSystem = {
  // Tipografía
  fonts: {
    sans: "var(--font-outfit)",
    mono: "var(--font-mono)",
  },

  // Paleta de colores — modifica aquí para cambiar todo el sistema
  colors: {
    // Primarios
    primary: {
      50:  "var(--color-primary-50)",
      100: "var(--color-primary-100)",
      500: "var(--color-primary-500)",
      600: "var(--color-primary-600)",
      900: "var(--color-primary-900)",
    },
    // Neutros
    neutral: {
      0:   "var(--color-neutral-0)",
      50:  "var(--color-neutral-50)",
      100: "var(--color-neutral-100)",
      200: "var(--color-neutral-200)",
      300: "var(--color-neutral-300)",
      500: "var(--color-neutral-500)",
      700: "var(--color-neutral-700)",
      900: "var(--color-neutral-900)",
    },
    // Semánticos
    success: "var(--color-success)",
    warning: "var(--color-warning)",
    error:   "var(--color-error)",
    info:    "var(--color-info)",
  },

  // Glassmorphism
  glass: {
    background: "var(--glass-background)",
    border:     "var(--glass-border)",
    blur:       "var(--glass-blur)",
    shadow:     "var(--glass-shadow)",
  },

  // Radios de borde
  radius: {
    sm:   "var(--radius-sm)",
    md:   "var(--radius-md)",
    lg:   "var(--radius-lg)",
    xl:   "var(--radius-xl)",
    full: "var(--radius-full)",
  },

  // Sombras
  shadows: {
    sm:    "var(--shadow-sm)",
    md:    "var(--shadow-md)",
    lg:    "var(--shadow-lg)",
    glass: "var(--shadow-glass)",
  },

  // Espaciado base — multiplica por este valor
  spacing: {
    base: 4, // px
  },

  // Transiciones
  transitions: {
    fast:   "var(--transition-fast)",
    normal: "var(--transition-normal)",
    slow:   "var(--transition-slow)",
  },
} as const;
