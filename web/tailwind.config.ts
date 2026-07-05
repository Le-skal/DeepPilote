import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Custom finance colors
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        bull: "hsl(var(--chart-bull))",
        bear: "hsl(var(--chart-bear))",
        // Neon violet theme colors
        neon: {
          violet: "hsl(var(--neon-violet))",
          fuchsia: "hsl(var(--neon-fuchsia))",
        },
        // Violet palette for direct use
        violet: {
          400: "#C084FC",
          500: "#A855F7",
          600: "#9333EA",
          700: "#7C3AED",
          800: "#6D28D9",
          900: "#5B21B6",
        },
        fuchsia: {
          400: "#E879F9",
          500: "#D946EF",
          600: "#C026D3",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
      },
      boxShadow: {
        glow: "0 0 25px -5px hsl(var(--primary) / 0.4)",
        "glow-sm": "0 0 15px -5px hsl(var(--primary) / 0.3)",
        "glow-lg": "0 0 40px -10px hsl(var(--primary) / 0.5)",
        "glow-success": "0 0 20px -5px hsl(var(--success) / 0.4)",
        "glow-danger": "0 0 20px -5px hsl(var(--destructive) / 0.4)",
        "glow-warning": "0 0 20px -5px hsl(var(--warning) / 0.4)",
        // Card shadows
        "card-hover": "0 8px 30px -10px hsl(var(--primary) / 0.25)",
        "card-active": "0 12px 40px -10px hsl(var(--primary) / 0.35)",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-violet": "linear-gradient(135deg, #A855F7 0%, #D946EF 100%)",
        "gradient-dark": "linear-gradient(180deg, hsl(260 30% 8%) 0%, hsl(260 30% 4%) 100%)",
      },
      animation: {
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
      },
      keyframes: {
        "glow-pulse": {
          "0%, 100%": {
            boxShadow: "0 0 15px -5px hsl(var(--primary) / 0.4)",
          },
          "50%": {
            boxShadow: "0 0 30px -5px hsl(var(--primary) / 0.6)",
          },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
