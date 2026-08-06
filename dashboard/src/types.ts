export type KENode = {
  id: string;
  kind: string;
  label: string;
  level?: number;
  source_ref?: string;
  community?: number;
};

export type LearningChapter = {
  id: string;
  title: string;
  question: string;
  outcome: string;
  conceptIds: string[];
  foundationConceptIds: string[];
  advancedConceptIds: string[];
  checkpointIds: string[];
  estimatedCoreMinutes: number;
  estimatedFullMinutes: number;
};

export type LearningPath = {
  version: number;
  reviewed: boolean;
  chapters: LearningChapter[];
};

export type CodeListing = {
  path: string;
  language: string;
  symbolKind: "file" | "class" | "function" | "method";
  startLine: number;
  endLine: number;
  previewEndLine: number;
  preview: string;
  full: string;
  rangeResolved: boolean;
};

export type KEEdge = {
  src: string;
  dst: string;
  kind: string;
  weight?: number;
  confidence?: string;
};

export type Insight = {
  severity: "HIGH" | "MED" | "LOW";
  rule: string;
  nodeId: string;
  text: string;
};
