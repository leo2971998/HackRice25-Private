import { Phone, ExternalLink } from "lucide-react";
import type { Source } from "@/lib/types";

export default function SourceCard({ s }: { s: Source }) {
  return (
    <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 p-4">
      <div className="flex items-center justify-between gap-2">
        <h4 className="font-semibold text-sm">{s.name}</h4>
        <div className="flex items-center gap-2">
          {s.url && (
            <a className="text-xs underline inline-flex items-center gap-1" href={s.url} target="_blank" rel="noreferrer">
              Website <ExternalLink size={14} />
            </a>
          )}
          {s.apply_url && (
            <a className="text-xs underline inline-flex items-center gap-1" href={s.apply_url} target="_blank" rel="noreferrer">
              Apply <ExternalLink size={14} />
            </a>
          )}
        </div>
      </div>
      {s.eligibility && <p className="mt-1 text-xs opacity-80">Eligibility: {s.eligibility}</p>}
      <div className="mt-2 flex flex-wrap gap-3 text-xs opacity-90">
        {s.phone && (
          <a href={`tel:${s.phone}`} className="inline-flex items-center gap-1 underline">
            <Phone size={14} /> {s.phone}
          </a>
        )}
        {s.county && <span>County: {s.county}</span>}
        {s.last_verified && <span>Verified: {s.last_verified}</span>}
      </div>
    </div>
  );
}