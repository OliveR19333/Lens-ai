import { useEffect, useRef } from 'react';
import anime from 'animejs';

export const useAnimationTimeline = (dependencies: any[] = []) => {
  const timelineRef = useRef<anime.AnimeTimelineInstance | null>(null);

  useEffect(() => {
    timelineRef.current = anime.timeline();
  }, dependencies);

  return timelineRef.current;
};

export const useReveal = (options?: anime.AnimeParams) => {
  const elementRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!elementRef.current) return;

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        anime({
          targets: elementRef.current,
          opacity: [0, 1],
          translateY: [20, 0],
          duration: 800,
          easing: 'easeOutQuad',
          ...options,
        });
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.1 });

    observer.observe(elementRef.current);

    return () => observer.disconnect();
  }, [options]);

  return elementRef;
};

export default useReveal;
