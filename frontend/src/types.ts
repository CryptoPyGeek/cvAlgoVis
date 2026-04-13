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
