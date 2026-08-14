# Embedded learning media in the dashboard

## Context

P3 now enriches every level 0-1 concept and requires each research note to
carry a `visual` or `lecture` — a blog explainer, a diagram, a recorded
lecture. Those resources are verified live (arXiv title match, dead-link HEAD,
YouTube oEmbed) and the page contract requires Go Deeper to link every one.

They are still only ever links. The owner wants images and diagrams embedded
from their online source wherever appropriate, so a reader sees the diagram
rather than a URL promising one.

## Global Constraints

- **Remote URLs originate from model output.** They are data, never
  instruction. Nothing may execute because a note said so.
- **No third-party JavaScript.** YouTube renders as its static thumbnail
  (`https://img.youtube.com/vi/<id>/hqdefault.jpg`) linking out to the video.
  No `<iframe>`, no embed script. An iframe would run third-party code inside
  the reader's dashboard to gain a play button.
- **Embed only what is verified to BE an image.** A URL is embeddable only if
  a HEAD request returns `content-type: image/*`. A blog post URL in an
  `<img>` tag renders as a broken icon; unverified URLs stay plain links.
- **Degrade to a link, never to nothing.** Any resource that cannot be
  embedded still appears as the Go Deeper link it already is.
- **Network calls are injectable.** Every check takes a `head=`/`get=`
  parameter so tests never leave the machine, matching `resources.py`.
- **Vitest runs `environment: "node"`.** Component tests use
  `renderToStaticMarkup`, never jsdom.
- **Do not overwrite `dashboard/src/data.gen.ts`.** It holds the committed SID
  bundle that vitest content assertions read. Build test bundles elsewhere.
- Known deployment limit to document, not solve: a strict Artifact CSP blocks
  all external hosts, so remote embeds render only in the local dashboard.

## Task 1: Load research notes from the wiki subdirectory

`dashboard/build_data.py::_load_notes` globs `Path(wiki_dir).glob("*.yaml")`,
but `research_mcp.wiki.wiki_put` writes to `<home>/_research_wiki/<slug>.yaml`.
The pipeline passes `--wiki-dir artifacts/<paper>-live/research_home`, so the
glob matches nothing and **zero notes reach the bundle** — verified against the
resnet and chain-of-thought bundles, which report `notes: 0` while both have a
note on disk.

Every research note ever produced has been invisible in the dashboard. This
blocks the rest of the plan: embeds are driven by note resources.

**Produces:** `_load_notes` finds notes whether they sit directly in
`wiki_dir` or in its `_research_wiki` subdirectory.

**Tests** (`dashboard/tests/test_build_notes.py`):
- a note in `<wiki_dir>/_research_wiki/x.yaml` reaches the returned notes dict
- a note directly in `<wiki_dir>/x.yaml` still does (older artifacts)
- the same slug in both places is loaded once, not duplicated
- a missing/empty wiki_dir still returns empty dicts, unchanged

Verify against real data: rebuilding the resnet bundle must report a non-zero
note count.

## Task 2: Classify a resource URL as embeddable

Add to `src/paper_skill/resources.py`:

```python
def embed_kind(url: str, head=requests.head) -> dict
```

Returns one of:
- `{"kind": "image", "src": <url>}` — HEAD returned `content-type: image/*`
- `{"kind": "video", "src": "https://img.youtube.com/vi/<id>/hqdefault.jpg",
   "href": <url>}` — a YouTube URL; `src` is the static thumbnail
- `{"kind": "link"}` — anything else, including unreachable hosts

Reuse the existing `_YOUTUBE` regex. Extract the video id from all three
forms: `watch?v=<id>`, `youtu.be/<id>`, `embed/<id>`.

An exception or a non-2xx status yields `{"kind": "link"}` — a checker that
cannot reach the host must never claim the resource is broken, matching how
`verify_resources` treats a 403.

**Tests** (extend `tests/test_resources.py`):
- `image/png` content-type → kind image, src is the url
- `text/html` content-type → kind link
- each of the three YouTube url forms → kind video with the right thumbnail
- a HEAD that raises → kind link, no exception escapes
- a non-http string (empty, `mailto:`) → kind link

## Task 3: Carry resource embeds into the bundle

In `dashboard/build_data.py`, add each note resource's embed classification so
the UI never needs a network call. Add a `--no-embed-probe` flag that skips the
HEAD requests and classifies every resource as `link`, so offline builds and
tests stay deterministic and fast.

**Produces:** every resource dict in `bundle["notes"][cid]["resources"]` gains
an `embed` key holding the Task 2 shape.

**Tests** (`dashboard/tests/test_build_embeds.py`):
- a note whose resource is an image gets `embed.kind == "image"`
- a YouTube resource gets `embed.kind == "video"` with the thumbnail src
- `--no-embed-probe` (or the injected probe) makes every embed `link` and
  performs no network call
- a note with no resources is unchanged
- resources keep their existing keys (url, title, type, why) untouched

## Task 4: Render the embeds

New pure component `dashboard/src/components/blocks/ResourceEmbed.tsx`
rendering one resource:

- `kind: "image"` → `<img>` with `loading="lazy"`, the resource title as
  `alt`, wrapped in a link to the original page, plus the `why` line as a
  caption.
- `kind: "video"` → the thumbnail `<img>` inside a link to `href`, with a
  visible play affordance drawn in CSS/SVG (no third-party embed) and the
  title and `why` beneath.
- `kind: "link"` → the existing plain link with its `why`.

Render `rel="noreferrer"` on every outbound link, and `referrerPolicy="no-referrer"`
on every remote `<img>`, so a third-party host is not told which page the
reader is on.

Wire it into the concept page's Go Deeper region so a concept with a note
shows its media. A concept without a note renders exactly as it does now.

**Tests** (`dashboard/src/components/blocks/ResourceEmbed.test.tsx`, node
environment, `renderToStaticMarkup`):
- an image resource renders an `<img>` whose src is the resource url
- a video resource renders the thumbnail src, and the anchor points at the
  watch url, and no `<iframe>` appears anywhere in the output
- a link resource renders an anchor and no `<img>`
- every remote img carries `referrerPolicy="no-referrer"`; every outbound
  anchor carries `rel` containing `noreferrer`
- a resource missing `why` renders without an empty caption element
