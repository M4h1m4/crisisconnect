import { MapPin } from "lucide-react";
import type { Resource } from "../types";

const CATEGORY_COLORS: Record<string, string> = {
  food: "bg-green-100 text-green-800",
  shelter: "bg-blue-100 text-blue-800",
  medical: "bg-red-100 text-red-800",
  emergency: "bg-orange-100 text-orange-800",
};

export function ResourceCard({ resource }: { resource: Resource }) {
  const color =
    CATEGORY_COLORS[resource.category] || "bg-gray-100 text-gray-800";

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900">{resource.name}</h4>
          <p className="mt-1 flex items-center gap-1 text-sm text-gray-600">
            <MapPin size={14} />
            {resource.address}
          </p>
        </div>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${color}`}
        >
          {resource.category}
        </span>
      </div>
      <div className="mt-2 flex items-center gap-3 text-xs text-gray-500">
        {resource.is_open !== null && (
          <span
            className={resource.is_open ? "text-green-600" : "text-red-500"}
          >
            {resource.is_open ? "Open now" : "Closed"}
          </span>
        )}
        {resource.rating && <span>★ {resource.rating}</span>}
        {resource.place_id && (
          <a
            href={`https://www.google.com/maps/place/?q=place_id:${resource.place_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            Get Directions
          </a>
        )}
      </div>
    </div>
  );
}
