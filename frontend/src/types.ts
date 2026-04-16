export type ParamDef = {
  name: string;
  type: "number";
  min: number;
  max: number;
  step: number;
  default: number;
  description?: string;
};

export type AlgorithmDef = {
  id: string;
  name: string;
  params: ParamDef[];
  snippet_available?: boolean;
};

export type ModuleDef = {
  id: string;
  name: string;
  algorithms: AlgorithmDef[];
};

export type LibraryDef = {
  id: string;
  name: string;
  enabled: boolean;
  input_kind?: "image" | "point_cloud";
  status_note?: string;
  modules: ModuleDef[];
};

export type CatalogResponse = {
  libraries: LibraryDef[];
};

export type ProcessResponse = {
  processed_image: string;
  meta: {
    elapsed_ms: number;
    width: number;
    height: number;
    algorithm: string;
  };
};

export type Open3DProcessResponse = {
  result_kind: "point_cloud_summary";
  summary: string;
  meta: {
    elapsed_ms: number;
    algorithm: string;
    filename: string;
    target_filename?: string | null;
    file_type: string;
    points_before: number;
    points_after: number;
  };
  stats: Record<string, string | number | boolean | number[] | number[][]>;
  source_points: [number, number, number][];
  target_points: [number, number, number][];
  processed_points: [number, number, number][];
};
