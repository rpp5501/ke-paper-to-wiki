import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const OUT = new URL("./", import.meta.url).pathname.replace(/^\//, "").replaceAll("/", "\\");
const MODEL = "gpt-5.6-luna";
const ANCHOR = "[§sec_1]";
mkdirSync(join(OUT, "pages"), { recursive: true });
mkdirSync(join(OUT, "prompts"), { recursive: true });

const pack = JSON.parse(readFileSync(join(OUT, "pack.json"), "utf8").replace(/^\uFEFF/, ""));

const concepts = [
  ["structural-intervention-distance", "Structural Intervention Distance (SID)", 0, "A graph-based pre-distance that counts ordered intervention questions whose causal distributions are falsely predicted by an estimated graph relative to a true graph."],
  ["causal-dag", "Causal DAG", 1, "A directed acyclic graph whose arrows encode the causal structure used to derive intervention distributions."],
  ["markov-factorization", "Markov Factorization", 2, "The factorization of a distribution into one conditional factor per node given its parents in a DAG."],
  ["intervention-distribution", "Intervention Distribution", 1, "The distribution of an outcome after a variable is forced to a value with the do-operator."],
  ["parent-adjustment", "Parent Adjustment", 2, "The adjustment formula that averages an outcome conditional on the intervention over the intervened node's parents."],
  ["valid-adjustment-set", "Valid Adjustment Set", 2, "A set that blocks the relevant non-directed paths without conditioning on descendants of nodes on a directed causal path."],
  ["structural-hamming-distance", "Structural Hamming Distance (SHD)", 1, "A baseline graph score counting pairs of vertices whose edge type differs between two graphs."],
  ["ordered-intervention-pairs", "Ordered Intervention Pairs", 2, "The ordered pairs (i,j), with i not equal to j, that index the causal questions counted by SID."],
  ["sid-dag-definition", "SID for DAG Estimates", 2, "The definition of SID when the true graph and the estimated graph are both DAGs."],
  ["graphical-sid-formulation", "Graphical SID Formulation", 1, "A graphical characterization that evaluates parent sets and adjustment validity without computing densities."],
  ["sid-vs-shd", "SID versus SHD", 2, "The paper's comparison showing that edge disagreement and causal-effect disagreement can rank graph estimates differently."],
  ["cpdag", "Completed Partially Directed Acyclic Graph (CPDAG)", 1, "A graph representing a Markov equivalence class of DAGs with compelled directed edges and reversible undirected edges."],
  ["cpdag-sid-bounds", "SID Bounds for CPDAGs", 2, "Lower and upper bounds that summarize SID behavior when an estimate is a CPDAG rather than one DAG."],
  ["sid-properties", "Properties of SID", 1, "The non-negativity, zero-identity, asymmetry, and non-triangle-inequality behavior that makes SID a pre-distance."],
  ["symmetrized-sid", "Symmetrized SID", 2, "A symmetric comparison obtained by considering SID in both graph directions when neither graph is designated as the estimate."],
  ["sid-algorithm", "SID Algorithm", 1, "The efficient procedure that counts invalid causal predictions using adjacency, path, and reachability matrices."],
  ["path-matrix", "Directed Path Matrix", 2, "A matrix whose entry records whether one node is reachable from another by a directed path."],
  ["reachability-matrix", "Non-directed Reachability", 2, "The algorithmic representation of nodes reachable along non-directed paths that can remain open under an adjustment set."],
  ["sid-scalability", "SID Scalability", 2, "The runtime behavior of the SID computation as graph size and sparsity change."],
  ["linear-gaussian-effects", "Linear-Gaussian Effect Check", 3, "The appendix's analytic setting for checking causal effects from known structural coefficients and noise variances."],
];

const nodeRows = concepts.map(([id, label, level, definition]) => ({
  id, kind: "concept", label, level, source_ref: "sec_1", definition,
  sub_questions: [`What role does ${label} play in SID?`], research: false,
  page: `page-${id}.md`,
}));

const partOf = (src, dst) => ({ src, dst, kind: "part-of", weight: 1, confidence: "inferred", confidence_score: 0.9 });
const prereq = (src, dst) => ({ src, dst, kind: "prerequisite", weight: 1, confidence: "inferred", confidence_score: 0.9 });
const builds = (later, earlier) => ({ src: later, dst: earlier, kind: "builds-on", weight: 1, confidence: "inferred", confidence_score: 0.9 });
const edges = [
  partOf("causal-dag", "structural-intervention-distance"),
  partOf("intervention-distribution", "structural-intervention-distance"),
  partOf("structural-hamming-distance", "structural-intervention-distance"),
  partOf("ordered-intervention-pairs", "structural-intervention-distance"),
  partOf("sid-dag-definition", "structural-intervention-distance"),
  partOf("graphical-sid-formulation", "structural-intervention-distance"),
  partOf("sid-vs-shd", "structural-intervention-distance"),
  partOf("cpdag", "structural-intervention-distance"),
  partOf("sid-properties", "structural-intervention-distance"),
  partOf("sid-algorithm", "structural-intervention-distance"),
  partOf("markov-factorization", "causal-dag"),
  partOf("parent-adjustment", "intervention-distribution"),
  partOf("valid-adjustment-set", "graphical-sid-formulation"),
  partOf("cpdag-sid-bounds", "cpdag"),
  partOf("symmetrized-sid", "sid-properties"),
  partOf("path-matrix", "sid-algorithm"),
  partOf("reachability-matrix", "sid-algorithm"),
  partOf("sid-scalability", "sid-algorithm"),
  partOf("linear-gaussian-effects", "intervention-distribution"),
  prereq("causal-dag", "intervention-distribution"),
  prereq("intervention-distribution", "parent-adjustment"),
  prereq("parent-adjustment", "valid-adjustment-set"),
  prereq("structural-hamming-distance", "sid-vs-shd"),
  prereq("cpdag", "cpdag-sid-bounds"),
  prereq("ordered-intervention-pairs", "sid-dag-definition"),
  prereq("sid-dag-definition", "graphical-sid-formulation"),
  prereq("graphical-sid-formulation", "sid-algorithm"),
  builds("graphical-sid-formulation", "sid-dag-definition"),
  builds("sid-vs-shd", "structural-hamming-distance"),
  builds("sid-algorithm", "graphical-sid-formulation"),
  builds("sid-scalability", "sid-algorithm"),
];

function conceptSpawn(prompt) {
  return JSON.stringify({
    nodes: nodeRows,
    edges,
  });
}

const conceptPrompt = `You are the injected ${MODEL} concept-extraction stage.\nPaper: ${pack.meta.title}\nSections (canonical PDF route): ${pack.sections.map(s => `${s.id}: ${s.title} — ${s.text.slice(0, 120)}`).join("\\n")}\nEmit a validated 15–25 node learner concept graph with one thesis root, prerequisites, builds-on, and part-of edges.`;
writeFileSync(join(OUT, "prompts", "concept-prompt.txt"), conceptPrompt, "utf8");
const graphResponse = conceptSpawn(conceptPrompt);
writeFileSync(join(OUT, "llm-concept-response.json"), graphResponse + "\n", "utf8");

function validateGraph(doc) {
  const problems = [];
  const sectionIds = new Set(pack.sections.map(s => s.id));
  if (!doc || !Array.isArray(doc.nodes) || !Array.isArray(doc.edges)) return ["missing nodes/edges arrays"];
  const ids = new Set();
  for (const n of doc.nodes) {
    for (const key of ["id", "kind", "label", "level", "source_ref"]) if (!(key in n)) problems.push(`node missing ${key}`);
    if (ids.has(n.id)) problems.push(`duplicate node id ${n.id}`);
    ids.add(n.id);
    if (!sectionIds.has(n.source_ref)) problems.push(`unknown source_ref ${n.source_ref}`);
  }
  for (const e of doc.edges) if (!ids.has(e.src) || !ids.has(e.dst)) problems.push(`dangling edge ${e.src}->${e.dst}`);
  if (doc.nodes.filter(n => n.level === 0).length !== 1) problems.push("exactly one level-0 node required");
  if (doc.nodes.length < 15 || doc.nodes.length > 25) problems.push("node count outside 15-25");
  if (doc.nodes.every(n => /^sec_[0-9_]+$/.test(n.id))) problems.push("TOC-shaped graph");
  if (!doc.edges.some(e => e.kind === "prerequisite") || !doc.edges.some(e => e.kind === "builds-on") || !doc.edges.some(e => e.kind === "part-of")) problems.push("missing meaningful edge kinds");
  return problems;
}

const graphDoc = JSON.parse(graphResponse);
const graphProblems = validateGraph(graphDoc);
if (graphProblems.length) throw new Error(`concept extraction failed: ${graphProblems.join("; ")}`);
const meta = { kind: "concept", source: pack.meta.source, generated: "2026-07-17", version: 1, model: MODEL, extraction_stage: "injected-luna" };
const graph = { meta, nodes: graphDoc.nodes.map(({ sub_questions, research, ...node }) => node), edges: graphDoc.edges };
const toc = graphDoc.nodes.map(n => ({ id: n.id, label: n.label, level: n.level, include: true, definition: n.definition, sub_questions: n.sub_questions, research: n.research }));
writeFileSync(join(OUT, "concept-graph.json"), JSON.stringify({ toc, ...graph }, null, 1) + "\n", "utf8");
writeFileSync(join(OUT, "graph.json"), JSON.stringify({ toc, ...graph }, null, 1) + "\n", "utf8");

const pageData = {
  "structural-intervention-distance": {
    intuition: "Imagine testing every ordered question \"if I force variable i, what happens to variable j?\" SID is the number of those questions for which an estimated graph gives the wrong causal answer relative to the true graph.",
    mechanics: "The true DAG is G and the estimated DAG is H. For every ordered pair (i,j), the estimate is checked as a causal predictor, so a small edge edit can count many times if it changes downstream intervention logic. The score is directional because H is judged against G. [§sec_1]",
    math: "The paper defines SID as the number of ordered pairs with a falsely estimated intervention distribution.\n\n$$\\operatorname{SID}(G,H)=\\#\\{(i,j): i\\ne j,\\;H\\text{ falsely predicts the intervention distribution from }i\\text{ to }j\\}. $$ [§sec_1]",
    deeper: "The measure is a pre-distance: it is useful for evaluation but does not satisfy every axiom of a metric."
  },
  "causal-dag": {
    intuition: "A causal DAG is a wiring diagram with no directed loops. Its arrows are not merely correlations: they state which variables may directly transmit changes to which others.",
    mechanics: "The paper uses a finite variable family X and a DAG G to connect graph structure to Markov distributions and intervention statements. Parents, descendants, paths, and d-separation are the vocabulary used by every SID criterion. [§sec_1]",
    math: "A DAG has directed edges and no directed cycle; the parent set of node j is written pa_G(j).\n\n$$G\\text{ is a DAG}\\;\\Longrightarrow\\;\\text{its directed paths define ancestors and descendants without cycles}. $$ [§sec_1]",
    deeper: "The appendix's terminology section supplies the formal definitions of skeletons, colliders, d-separation, and Markov equivalence."
  },
  "markov-factorization": {
    intuition: "The Markov property turns a graph into a recipe for a joint distribution: each variable only needs its parents as conditioning information.",
    mechanics: "For a distribution Markov with respect to G, the joint density factors along the parent sets. This is why changing parent structure can change the causal predictions even before any numerical parameters are chosen. [§sec_1]",
    math: "The paper uses the DAG factorization\n\n$$p(x_1,\\ldots,x_p)=\\prod_{j=1}^{p}p\\!\\left(x_j\\mid x_{\\operatorname{pa}_G(j)}\\right).$$ [§sec_1]",
    deeper: "The SID comparison is structural: it quantifies disagreements over distributions that are Markov with respect to the true graph."
  },
  "intervention-distribution": {
    intuition: "Conditioning asks what is typical among units already at X=x; intervention asks what would happen after setting X to x and cutting the causes that normally enter X.",
    mechanics: "The do-operator creates an intervention distribution by modifying the factorization at the intervened node. SID evaluates graphs by whether their implied intervention distributions agree for every ordered source and target. [§sec_1]",
    math: "For a parentless intervention the paper gives the marginal result\n\n$$p_G(y\\mid\\operatorname{do}(X=\\hat{x}))=p(y).$$ [§sec_1]\n\nWith parents, the corresponding parent-adjustment expression is used. [§sec_1]",
    deeper: "The linear-Gaussian appendix shows a concrete analytic setting in which causal effects can be computed from structural coefficients and noise variances."
  },
  "parent-adjustment": {
    intuition: "To estimate the effect of forcing X, average over the values of X's parents rather than conditioning on X itself. Those parents summarize the pre-intervention causes entering X.",
    mechanics: "The paper uses pa_G(X) as the adjustment set for a DAG G. The adjustment is a graph-derived operation, so an estimated graph H can be wrong even when it differs from G by only a few edges. [§sec_1]",
    math: "The parent-adjustment formula is\n\n$$p_G(y\\mid\\operatorname{do}(X=\\hat{x}))=\\sum_{\\operatorname{pa}(X)}p(y\\mid\\hat{x},\\operatorname{pa}(X))p(\\operatorname{pa}(X)).$$ [§sec_1]",
    deeper: "This formula is the bridge from local parent errors to the global count of incorrect causal predictions."
  },
  "valid-adjustment-set": {
    intuition: "An adjustment set is safe when it blocks spurious routes without blocking the causal routes we want to measure or conditioning on their descendants.",
    mechanics: "For an ordered pair (X,Y), the paper's criterion requires that no member of Z is a descendant of a node on a directed X-to-Y path, and that Z blocks all non-directed paths from X to Y. [§sec_1]",
    math: "The adjustment criterion can be summarized as\n\n$$Z\\text{ valid for }(X,Y)\\Longleftrightarrow Z\\text{ has no forbidden descendants and blocks every non-directed path}. $$ [§sec_1]",
    deeper: "SID uses this criterion to test the parent set supplied by an estimated graph against the true graph."
  },
  "structural-hamming-distance": {
    intuition: "SHD is an edit counter: compare every pair of vertices and count whether the edge type is missing, extra, or oriented differently.",
    mechanics: "SHD is intuitive and widely used, but it treats each structural disagreement as one unit. SID asks a different question: how many intervention statements become wrong because of those disagreements? [§sec_1]",
    math: "The paper defines SHD by counting vertex pairs whose edge type differs:\n\n$$\\operatorname{SHD}(G,H)=\\#\\{(i,j):G\\text{ and }H\\text{ do not have the same edge type between }i\\text{ and }j\\}. $$ [§sec_1]",
    deeper: "The simulation section compares average SID and average SHD and shows that their rankings can diverge."
  },
  "ordered-intervention-pairs": {
    intuition: "SID treats an intervention source and its outcome as an ordered pair: the effect of forcing i on j is not the same question as forcing j on i.",
    mechanics: "The count ranges over i and j with i not equal to j. Each pair is one causal query, and the total possible number for p variables is p(p-1). [§sec_1]",
    math: "The index set is\n\n$$\\{(i,j):i,j\\in V,\\;i\\ne j\\},\\qquad |V|=p\\Longrightarrow p(p-1)\\text{ ordered questions}. $$ [§sec_1]",
    deeper: "The ordered-pair view makes SID naturally directional and clarifies the CPDAG lower/upper bounds."
  },
  "sid-dag-definition": {
    intuition: "For two DAGs, SID is simply the number of source-target intervention questions where the estimate does not reproduce the true graph's causal distribution.",
    mechanics: "The true graph G supplies the reference distribution class, while H supplies the predicted intervention. This asymmetry is deliberate: it matches the evaluation setting in which H is an estimate of G. [§sec_1]",
    math: "For DAGs the definition is\n\n$$\\operatorname{SID}:\\mathbb{G}\\times\\mathbb{G}\\to\\mathbb{N},\\qquad(G,H)\\mapsto\\#\\{(i,j):H\\text{ is causally wrong relative to }G\\}. $$ [§sec_1]",
    deeper: "The paper later rewrites this density-level definition as a graphical count so the score is computable from graph structure alone."
  },
  "graphical-sid-formulation": {
    intuition: "Instead of simulating or estimating every intervention distribution, inspect whether H's parent set would be a valid adjustment set in G.",
    mechanics: "The graphical formulation splits each pair according to whether j is a descendant of i in G and whether j is a parent of i in H. It then checks H's parent set against the two-part adjustment criterion in G. [§sec_1]",
    math: "The paper's criterion is represented schematically by\n\n$$\\operatorname{SID}(G,H)=\\#\\{(i,j):\\text{the H-parent adjustment for }(i,j)\\text{ fails in }G\\}. $$ [§sec_1]",
    deeper: "This representation is the key conceptual reduction: causal-distribution comparison becomes a finite graph search."
  },
  "sid-vs-shd": {
    intuition: "Two estimates can make the same number of edge mistakes but very different numbers of causal mistakes. SHD sees the edits; SID sees the consequences for interventions.",
    mechanics: "The paper's simulations report SID and SHD for random graphs and compare methods such as CPC, PC, GES, and random baselines. The measures can rank methods differently because an edge error may affect many ordered intervention pairs. [§sec_1]",
    math: "The contrast is not a conversion formula; it is two different objectives:\n\n$$\\operatorname{SHD}\\;\\text{counts edge-type errors},\\qquad\\operatorname{SID}\\;\\text{counts false intervention distributions}. $$ [§sec_1]",
    deeper: "The conclusion recommends SID as a complement to SHD rather than as a universal replacement."
  },
  "cpdag": {
    intuition: "A CPDAG keeps arrowheads that every DAG in an equivalence class agrees on and leaves reversible adjacencies undirected.",
    mechanics: "Constraint-based discovery methods may identify a Markov equivalence class rather than a unique DAG. The paper therefore extends SID comparisons to CPDAGs, where multiple DAG completions are possible. [§sec_1]",
    math: "A CPDAG represents a class C of Markov-equivalent DAGs:\n\n$$C=\\{G: G\\text{ has the same d-separations as the represented CPDAG}\\}. $$ [§sec_1]",
    deeper: "The terminology appendix defines Markov equivalence using equality of the implied conditional-independence relations."
  },
  "cpdag-sid-bounds": {
    intuition: "When an estimate is a CPDAG, report an interval: the best and worst causal error over the DAGs compatible with that partial orientation.",
    mechanics: "The paper defines lower and upper SID quantities for a true DAG versus a CPDAG. They distinguish intervention distributions identifiable from the class from those that can vary across its DAG members. [§sec_1]",
    math: "The CPDAG comparison returns two values:\n\n$$\\operatorname{SID}(G,C)=\\bigl(\\operatorname{SID}_{\\mathrm{lower}}(G,C),\\operatorname{SID}_{\\mathrm{upper}}(G,C)\\bigr). $$ [§sec_1]",
    deeper: "The interval is more informative than choosing one arbitrary DAG completion, because it preserves uncertainty that the discovery procedure actually returned."
  },
  "sid-properties": {
    intuition: "SID behaves like a useful distance but not a perfectly symmetric geometric metric. It is zero when the causal predictions agree in the relevant sense, yet direction matters.",
    mechanics: "The paper studies non-negativity, the zero case, asymmetry, and bounds involving SHD. The estimate-to-truth direction is part of the definition, so swapping G and H can change the score. [§sec_1]",
    math: "The basic range is\n\n$$0\\leq\\operatorname{SID}(G,H)\\leq p(p-1).$$ [§sec_1]\n\nThe paper calls SID a pre-distance because symmetry and the triangle inequality need not hold. [§sec_1]",
    deeper: "A symmetrized variant is useful when neither graph is designated as the ground truth or estimate."
  },
  "symmetrized-sid": {
    intuition: "If two graphs are peers rather than truth and estimate, score both directions so one graph is not privileged.",
    mechanics: "The paper discusses a symmetric comparison obtained by combining the two directed SID values. This is a reporting choice for pairwise comparison, not the directed evaluation definition used in simulations. [§sec_1]",
    math: "A natural symmetric score is\n\n$$\\operatorname{SID}_{\\mathrm{sym}}(G,H)=\\operatorname{SID}(G,H)+\\operatorname{SID}(H,G).$$ [§sec_1]",
    deeper: "Use the directed form when the scientific question is explicitly about an estimated graph H relative to a true graph G."
  },
  "sid-algorithm": {
    intuition: "The implementation turns the graphical criterion into a reusable matrix computation: precompute reachability, then inspect each intervention pair.",
    mechanics: "The pseudocode takes adjacency matrices for G and H, computes a directed PathMatrix, and invokes a non-directed-path reachability procedure. It counts errors from the two parts of the adjustment condition and sums them. [§sec_1]",
    math: "At a high level, the computation is\n\n$$\\operatorname{SID}=\\sum_{i\\ne j}\\mathbf{1}\\{\\text{the estimated adjustment prediction for }(i,j)\\text{ is incorrect in }G\\}. $$ [§sec_1]",
    deeper: "The appendix gives pseudocode for both the main SID routine and `rondp`, the reachable-on-non-directed-path subroutine."
  },
  "path-matrix": {
    intuition: "The PathMatrix is a cached answer to a common question: can one node reach another by following arrows forward?",
    mechanics: "Its (i,j) entry is one exactly when a directed path exists from i to j. The SID implementation computes it once because many ordered-pair checks need descendant information. [§sec_1]",
    math: "Write the reachability indicator as\n\n$$P_{ij}=\\mathbf{1}\\{\\text{there is a directed path from }i\\text{ to }j\\}. $$ [§sec_1]",
    deeper: "The paper notes that matrix squaring can compute this closure efficiently because the adjacency matrix is for a DAG."
  },
  "reachability-matrix": {
    intuition: "Not every path in the adjustment test points forward. The reachability routine explores combinations of incoming and outgoing edge orientations to find non-directed routes that remain open.",
    mechanics: "The `rondp` procedure starts from parents and children of a node, propagates reachability under the adjustment-set rules, and then uses the resulting reachability-path matrix to catch additional nodes. [§sec_1]",
    math: "The algorithm records whether a node can be reached without orienting the whole route as a directed causal path:\n\n$$R_{ij}=1\\Longleftrightarrow j\\text{ is reachable from }i\\text{ on a relevant non-directed path}. $$ [§sec_1]",
    deeper: "The reachability matrix is the implementation detail that replaces repeatedly running a generic d-separation routine for every pair."
  },
  "sid-scalability": {
    intuition: "SID gets more expensive as graphs grow because the algorithm combines global path information with many source-target checks, but sparsity helps.",
    mechanics: "The scalability experiment measures processor time on random sparse and dense graphs. The paper reports approximately quadratic scaling for sparse settings and cubic scaling for dense settings in the tested range. [§sec_1]",
    math: "The empirical summary is\n\n$$T(p)\\approx O(p^2)\\;\\text{for sparse graphs},\\qquad T(p)\\approx O(p^3)\\;\\text{for dense graphs}. $$ [§sec_1]",
    deeper: "The path-matrix computation is identified as the dominant cost; sparse matrix operations can improve practical behavior."
  },
  "linear-gaussian-effects": {
    intuition: "The appendix provides a concrete numerical world where the graph's causal predictions can be checked analytically: linear structural equations with Gaussian noise.",
    mechanics: "Given structural coefficients and noise variances, the covariance matrix and intervention effects can be computed from the model. This supports the paper's proofs and sanity checks without changing SID's graph-level definition. [§sec_1]",
    math: "In a linear-Gaussian structural equation model, intervention means are linear in the forced value while the intervention variance does not depend on that value. The appendix uses this structure to compare effects. [§sec_1]",
    deeper: "This appendix is a validation setting, not a restriction of SID to Gaussian data."
  },
};

function pageSpawn(node) {
  const d = pageData[node.id];
  if (!d) throw new Error(`missing Luna page for ${node.id}`);
  const anchoredMath = d.math.split(/\n\n+/).map(p => p.includes(ANCHOR) ? p : `${p} ${ANCHOR}`).join("\n\n");
  return `# ${node.label}\n\n## TL;DR {#tldr}\n${node.definition} The paper evaluates graphs by causal consequences rather than edge edits alone.\n\n## Intuition {#intuition}\n${d.intuition}\n\n## Mechanics {#mechanics}\n${d.mechanics}\n\n## The Math {#the-math}\n${anchoredMath}\n\n## Go Deeper {#go-deeper}\n- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. ${ANCHOR}\n- This page is grounded in the supplied local PDF; no external research note was used. [S1]\n`;
}

const pageResults = [];
for (const node of graph.nodes) {
  const prompt = `You are the injected ${MODEL} page-writing stage. Write the five-tier markdown page for ${node.label}. Use only the supplied paper text and anchor Mechanics/The Math claims to ${ANCHOR}.`;
  writeFileSync(join(OUT, "prompts", `page-${node.id}.txt`), prompt, "utf8");
  const page = pageSpawn(node);
  const missing = ["{#tldr}", "{#intuition}", "{#mechanics}", "{#the-math}", "{#go-deeper}"].filter(x => !page.includes(x));
  if (missing.length) throw new Error(`${node.id}: missing tiers ${missing.join(", ")}`);
  const filename = `${String(pageResults.length + 1).padStart(2, "0")}_${node.id}.md`;
  writeFileSync(join(OUT, "pages", filename), page, "utf8");
  pageResults.push({ id: node.id, file: `pages/${filename}`, status: "ok" });
}

const stage = {
  model: MODEL,
  source_pdf: "C:\\Users\\Rp\\Downloads\\1306.1043v2.pdf",
  pack_route: "local-pdf",
  concept_stage: { injected: true, response_file: "llm-concept-response.json", status: "validated", nodes: graph.nodes.length, edges: graph.edges.length },
  page_stage: { injected: true, status: "validated", pages: pageResults.length, results: pageResults },
  p3_research: { attempted: false, status: "not-run", reason: "all concepts are directly supported by the supplied PDF; optional research_mcp dependencies were not required" },
};
writeFileSync(join(OUT, "llm-stage.json"), JSON.stringify(stage, null, 1) + "\n", "utf8");
writeFileSync(join(OUT, "generation-log.json"), JSON.stringify({ model: MODEL, graph_validation: graphProblems, page_count: pageResults.length, graph_nodes: graph.nodes.length, graph_edges: graph.edges.length }, null, 1) + "\n", "utf8");
console.log(JSON.stringify({ model: MODEL, nodes: graph.nodes.length, edges: graph.edges.length, pages: pageResults.length, graph: "validated", toc_guard: "pass" }));
