import { create } from "zustand";

export type View = "concepts" | "clusters" | "code" | "bridged";
export type LayoutPhase = "loading" | "ready" | "empty" | "error";
export type PendingNavigation = {
  requestId: number;
  nodeId: string;
  requiredView: View;
};
export type PlayerState = {
  steps: string[];
  idx: number;
  label: string;
} | null;

export interface AppState {
  selected: string | null;
  setSelected: (id: string | null) => void;
  view: View;
  setView: (view: View) => void;
  hiddenKinds: Set<string>;
  toggleKind: (kind: string) => void;
  blastOn: boolean;
  setBlastOn: (blastOn: boolean) => void;
  hoverEq: string | null;
  setHoverEq: (id: string | null) => void;
  player: PlayerState;
  setPlayer: (player: PlayerState) => void;
  step: (direction: 1 | -1) => void;
  tourIdx: number | null;
  setTourIdx: (index: number | null) => void;
  sidebarTab: "insights" | "trace";
  setSidebarTab: (tab: "insights" | "trace") => void;
  layoutPhase: LayoutPhase;
  setLayoutPhase: (phase: LayoutPhase) => void;
  navigationRequestId: number;
  pendingNavigation: PendingNavigation | null;
  queueNavigation: (nodeId: string, requiredView: View) => void;
  clearNavigation: (requestId: number) => void;
}

export const useApp = create<AppState>((set) => ({
  selected: null,
  setSelected: (selected) => set({ selected }),
  view: "concepts",
  setView: (view) => set({ view }),
  hiddenKinds: new Set(),
  toggleKind: (kind) =>
    set((state) => {
      const hiddenKinds = new Set(state.hiddenKinds);
      if (hiddenKinds.has(kind)) hiddenKinds.delete(kind);
      else hiddenKinds.add(kind);
      return { hiddenKinds };
    }),
  blastOn: false,
  setBlastOn: (blastOn) => set({ blastOn }),
  hoverEq: null,
  setHoverEq: (hoverEq) => set({ hoverEq }),
  player: null,
  setPlayer: (player) => set({ player }),
  step: (direction) =>
    set((state) => {
      if (!state.player) return {};
      const lastIndex = Math.max(state.player.steps.length - 1, 0);
      return {
        player: {
          ...state.player,
          idx: Math.min(Math.max(state.player.idx + direction, 0), lastIndex),
        },
      };
    }),
  tourIdx: null,
  setTourIdx: (tourIdx) => set({ tourIdx }),
  sidebarTab: "insights",
  setSidebarTab: (sidebarTab) => set({ sidebarTab }),
  layoutPhase: "loading",
  setLayoutPhase: (layoutPhase) => set({ layoutPhase }),
  navigationRequestId: 0,
  pendingNavigation: null,
  queueNavigation: (nodeId, requiredView) =>
    set((state) => {
      if (state.layoutPhase !== "ready") return {};
      const requestId = state.navigationRequestId + 1;
      return {
        navigationRequestId: requestId,
        pendingNavigation: { requestId, nodeId, requiredView },
        view: requiredView,
      };
    }),
  clearNavigation: (requestId) =>
    set((state) => (
      state.pendingNavigation?.requestId === requestId
        ? { pendingNavigation: null }
        : {}
    )),
}));
