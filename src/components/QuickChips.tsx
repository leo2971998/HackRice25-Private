const presets = [
  "Rent help in Houston",
  "Utility assistance Harris County",
  "How to apply for SNAP in Texas",
  "First-time homebuyer Houston"
];

export default function QuickChips({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {presets.map((p) => (
        <button 
          key={p} 
          onClick={() => onPick(p)} 
          className="rounded-xl border-2 border-blue-200 bg-blue-50 hover:bg-blue-100 hover:border-blue-300 px-4 py-3 text-sm font-medium text-blue-700 transition-all duration-200 text-left hover:shadow-md"
        >
          {p}
        </button>
      ))}
    </div>
  );
}