# Knowledge Dashboard

Internet-disconnected localhost dashboard for Knowledge-Engine paper, code, and bridged graphs.

## Development

Install the local JavaScript dependencies, generate the static data module, run the tests, and start Vite:

```powershell
npm install
python build_data.py --graph ..\fixtures\aiayn_concept_graph.json --pack ..\fixtures\aiayn_tiny_pack.json --pages-dir ..\fixtures\pages --wiki-dir ..\fixtures\wiki
npm test
npm run dev
```

Open the localhost URL printed by Vite. The development server is local infrastructure, not an application backend.

## Production build

```powershell
npm run build
python -m http.server -d dist 8000
```

Open `http://localhost:8000/`.

The dashboard remains 100% disconnected from the internet: it makes no external API or CDN requests and performs no runtime data fetch. Graph data, application assets, KaTeX styles/fonts, and the ELK layout worker are emitted locally by the build.

## Attribution

UI paradigms and component patterns are adapted from [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) (MIT)—guided tour, layer legend, filter panel, and explain drawer—and [TrueCourse](https://github.com/truecourse-ai/truecourse) (MIT)—insights sidebar, context switcher, trace player, and diff/staleness paradigms.

The repository-level `/explain` skill is adapted from Understand-Anything's `understand-explain` skill (MIT).
