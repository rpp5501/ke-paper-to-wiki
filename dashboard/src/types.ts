export type KENode = {
  id: string;
  kind: string;
  label: string;
  level?: number;
  source_ref?: string;
  community?: number;
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
