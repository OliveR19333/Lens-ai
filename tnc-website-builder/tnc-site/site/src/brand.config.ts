export interface BrandConfig {
  name: string;
  description: string;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    text: string;
    bg: string;
  };
  fonts: {
    family: string;
    headingFamily?: string;
  };
  radius: string;
  motionIntensity: "minimal" | "standard" | "intense";
}

export const defaultBrandConfig: BrandConfig = {
  name: "TNC",
  description: "Beautiful, intelligent digital experiences for forward-thinking brands",
  colors: {
    primary: "#1f2937",      // Dark slate
    secondary: "#6366f1",    // Indigo
    accent: "#ec4899",       // Pink
    text: "#111827",
    bg: "#ffffff",
  },
  fonts: {
    family: "'Inter', sans-serif",
    headingFamily: "'Poppins', sans-serif",
  },
  radius: "0.5rem",
  motionIntensity: "standard",  // Motion tier intensity
};

export const applyBrandConfig = (config: BrandConfig) => {
  const root = document.documentElement;
  root.style.setProperty("--color-primary", config.colors.primary);
  root.style.setProperty("--color-secondary", config.colors.secondary);
  root.style.setProperty("--color-accent", config.colors.accent);
  root.style.setProperty("--color-text", config.colors.text);
  root.style.setProperty("--color-bg", config.colors.bg);
  root.style.setProperty("--font-family", config.fonts.family);
  root.style.setProperty("--heading-family", config.fonts.headingFamily || config.fonts.family);
  root.style.setProperty("--radius", config.radius);
  root.style.setProperty("--motion-intensity", config.motionIntensity === "minimal" ? "0.5" : config.motionIntensity === "intense" ? "1.5" : "1");
};

export default defaultBrandConfig;
