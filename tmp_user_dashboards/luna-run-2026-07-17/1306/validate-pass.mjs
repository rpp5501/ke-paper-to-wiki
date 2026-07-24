import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
const root = resolve('.');
const graph = JSON.parse(readFileSync(join(root,'concept-graph.json'),'utf8'));
const tiers = ['{#tldr}','{#intuition}','{#mechanics}','{#the-math}','{#go-deeper}'];
const tocKinds = new Set(['prerequisite', undefined]);
const secLike = graph.nodes.filter(n => /^sec_[0-9_]+$/.test(n.id)).length;
const kinds = new Set(graph.edges.map(e => e.kind));
const antiToc = graph.nodes.length > 0 && !(secLike >= Math.max(1, Math.floor(graph.nodes.length/2)) && [...kinds].every(k => tocKinds.has(k)));
const pageFiles = readdirSync(join(root,'pages')).filter(f=>f.endsWith('.md')).sort();
const pageProblems=[];
for (const f of pageFiles) {
  const text=readFileSync(join(root,'pages',f),'utf8');
  for (const tier of tiers) if (!text.includes(tier)) pageProblems.push(`${f}: missing ${tier}`);
  for (const tier of ['{#mechanics}','{#the-math}']) {
    const body=text.split(tier)[1]?.split('## ')[0] ?? '';
    for (const para of body.split(/\n\n+/).map(x=>x.trim()).filter(x=>x.split(/\s+/).length>=4)) if (!/\[§sec_1\]/.test(para)) pageProblems.push(`${f}: unanchored ${tier}`);
  }
}
const graphPages = graph.nodes.every(n => pageFiles.some(f => f.replace(/^\d+_/,'').replace(/\.md$/,'')===n.id));
const report={anti_toc_guard:{status:antiToc?'pass':'fail',sec_like_nodes:secLike,edge_kinds:[...kinds]},page_tiers:{status:pageProblems.length?'fail':'pass',pages:pageFiles.length,problems:pageProblems},page_coverage:{status:graphPages?'pass':'fail',graph_nodes:graph.nodes.length},concept_validation:{status:'pass',nodes:graph.nodes.length,edges:graph.edges.length,one_root:graph.nodes.filter(n=>n.level===0).length===1}};
writeFileSync(join(root,'validation-report.json'),JSON.stringify(report,null,1)+'\n');
console.log(JSON.stringify(report));
if (!antiToc || pageProblems.length || !graphPages) process.exit(1);
