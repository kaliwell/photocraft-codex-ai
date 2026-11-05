# Project data paths

Saved projects use `<full-project-filename>.photocraft-data/` beside the project file. Keeping the extension separates similarly named PSD, PNG and PCraft projects.

- `history/<id>/snapshot.json` and `references/` hold prompt/reference snapshots. Retention is **per project**: 50 entries / 512 MiB. Restore is read-only and identical snapshots are reused.
- `cutting/plan.json` automatically persists cut lines. Identical canvases in different projects remain isolated; incompatible canvas sizes do not reuse a plan.
- **Export plan** writes `cutting/longpiccutter.json`. PNG ZIP export still asks for its destination.
- Save an untitled project before storing history. Unsaved cutting plans remain in the current window; manual JSON export is available.
- Switching documents changes history scope and discards stale asynchronous history responses. Reopen the cutter to load that project's plan.
- Save As starts a new history scope, retaining the old project's history. An open cutter carries its current lines into the new project's data directory.
- Move the project file and its adjacent data directory together. When renaming the project manually, rename its data directory to match.
- Legacy global history and cutter caches remain untouched; they are not automatically assigned to a project.
