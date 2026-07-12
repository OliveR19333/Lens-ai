import { useReveal } from "@/hooks/useAnimationTimeline";

interface TextRevealProps {
  text: string;
  className?: string;
  delay?: number;
}

export const TextReveal = ({ text, className = "", delay = 0 }: TextRevealProps) => {
  const ref = useReveal({ delay });

  return (
    <span ref={ref} className={className}>
      {text}
    </span>
  );
};
