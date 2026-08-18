export type ElementRef = { revisionId: string; globalId: string };
export type ColorRule = { elementRefs: ElementRef[]; cssColor: string; opacity?: number };
export type Viewpoint = { camera: unknown; clippingPlanes?: unknown[]; selected?: ElementRef[] };

export interface ViewerAdapter {
  loadRevision(revisionId: string, artifactUrl: string): Promise<void>;
  unloadRevision(revisionId: string): Promise<void>;
  select(elements: ElementRef[]): Promise<void>;
  isolate(elements: ElementRef[]): Promise<void>;
  clearIsolation(): Promise<void>;
  applyColors(rules: ColorRule[]): Promise<void>;
  fitTo(elements: ElementRef[]): Promise<void>;
  getViewpoint(): Promise<Viewpoint>;
  restoreViewpoint(viewpoint: Viewpoint): Promise<void>;
  dispose(): Promise<void>;
}
