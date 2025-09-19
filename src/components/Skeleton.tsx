// src/components/Skeleton.tsx
import clsx from "clsx";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return <div className={clsx("animate-pulse bg-dark-400/60 rounded", className)} />;
}

interface SkeletonGroupProps {
  count: number;
  className?: string;
  itemClassName?: string;
}

export function SkeletonGroup({ count, className, itemClassName }: SkeletonGroupProps) {
  return (
    <div className={clsx("space-y-3", className)}>
      {Array.from({ length: count }).map((_, index) => (
        <Skeleton key={index} className={itemClassName} />
      ))}
    </div>
  );
}

