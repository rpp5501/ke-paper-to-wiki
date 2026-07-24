export const NODE_CARD_WIDTH = 220;
export const NODE_MIN_HEIGHT = 72;

const CHARACTERS_PER_LINE = 24;
const LABEL_LINE_HEIGHT = 18;
const CARD_CHROME_HEIGHT = 54;

export function estimatedLabelLines(label: string): number {
  const words = label.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) return 1;

  let lines = 1;
  let used = 0;
  for (const word of words) {
    const chunks = Math.max(1, Math.ceil(word.length / CHARACTERS_PER_LINE));
    if (chunks > 1) {
      if (used > 0) lines += 1;
      lines += chunks - 1;
      used = word.length % CHARACTERS_PER_LINE;
    } else if (used === 0 || used + 1 + word.length <= CHARACTERS_PER_LINE) {
      used += (used > 0 ? 1 : 0) + word.length;
    } else {
      lines += 1;
      used = word.length;
    }
  }
  return lines;
}

export function nodeCardSize(label: string): { width: number; height: number } {
  return {
    width: NODE_CARD_WIDTH,
    height: Math.max(
      NODE_MIN_HEIGHT,
      CARD_CHROME_HEIGHT + estimatedLabelLines(label) * LABEL_LINE_HEIGHT,
    ),
  };
}
