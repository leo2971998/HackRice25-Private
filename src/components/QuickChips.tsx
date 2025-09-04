const presets = [
  "Rent help in Houston",
  "Utility assistance Harris County",
  "How to apply for SNAP in Texas",
  "First-time homebuyer Houston"
];

export default function QuickChips({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {presets.map((p) => (
        <button key={p} onClick={() => onPick(p)} className="rounded-full border border-neutral-300 dark:border-neutral-700 px-3 py-1 text-xs hover:bg-neutral-100 dark:hover:bg-neutral-900">
          {p}
        </button>
      ))}
    </div>
  );
}