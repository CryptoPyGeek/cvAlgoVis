import type { LibraryDef } from "../types";

type Props = {
  libraries: LibraryDef[];
  value: string;
  onChange: (libraryId: string) => void;
};

export function LibrarySelector({ libraries, value, onChange }: Props) {
  return (
    <label>
      库
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {libraries.map((library) => (
          <option key={library.id} value={library.id} disabled={!library.enabled}>
            {library.name}
            {!library.enabled ? " (预留)" : ""}
          </option>
        ))}
      </select>
    </label>
  );
}
