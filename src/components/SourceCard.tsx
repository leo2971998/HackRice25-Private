import { Phone, ExternalLink, MapPin, Calendar } from "lucide-react";
import type { Source } from "@/lib/types";

export default function SourceCard({ s }: { s: Source }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-3">
        <h4 className="font-semibold text-gray-900 text-sm leading-tight">{s.name}</h4>
        <div className="flex items-center gap-2 flex-shrink-0">
          {s.url && (
            <a 
              className="text-xs text-blue-600 hover:text-blue-800 underline inline-flex items-center gap-1 transition-colors" 
              href={s.url} 
              target="_blank" 
              rel="noreferrer"
            >
              Website <ExternalLink size={12} />
            </a>
          )}
          {s.apply_url && (
            <a 
              className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded-md inline-flex items-center gap-1 transition-colors" 
              href={s.apply_url} 
              target="_blank" 
              rel="noreferrer"
            >
              Apply <ExternalLink size={12} />
            </a>
          )}
        </div>
      </div>
      
      {s.eligibility && (
        <p className="text-xs text-gray-600 mb-3 bg-gray-50 rounded-lg p-2">
          <span className="font-medium">Eligibility:</span> {s.eligibility}
        </p>
      )}
      
      <div className="flex flex-wrap gap-3 text-xs text-gray-500">
        {s.phone && (
          <a href={`tel:${s.phone}`} className="inline-flex items-center gap-1 text-green-600 hover:text-green-800 transition-colors">
            <Phone size={12} /> {s.phone}
          </a>
        )}
        {s.county && (
          <span className="inline-flex items-center gap-1">
            <MapPin size={12} /> {s.county}
          </span>
        )}
        {s.last_verified && (
          <span className="inline-flex items-center gap-1">
            <Calendar size={12} /> Verified: {s.last_verified}
          </span>
        )}
      </div>
    </div>
  );
}