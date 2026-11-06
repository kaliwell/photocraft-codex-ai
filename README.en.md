# PhotoCraft · Codex AI

New **Detail page base**: analyze complete long pages through numbered crops and reconstruct editable text, shapes and borders in a long PSD, excluding products and photographs. Supports height up to 30000 pixels; see the [English guide](docs/usage-en.md).

**PSD settings** now supports target pixel dimensions, aspect ratios, DPI and font family for reference-to-PSD reconstruction, including recomposing square references into 1:2 layouts. Settings are included in history. See the [English guide](docs/usage-en.md#6-reference-to-psd-base-layout).

[中文](README.md) · [Illustrated guide](docs/usage-en.md) · [Project data paths](docs/project-data-en.md)

**Native selection AI, references, long-image cutting and canvas clipboard export.**

Screenshots show the unified development build; the published v0.4.0 ZIP predates some features below.

## Screenshots

![Selection AI and references](examples/usage/en/references.png)

![Full-image view in the long-image cutter](examples/usage/en/cutter.png)

![Project history](examples/usage/en/history.png)

## Usage

**Current unified development build:** one PhotoCraft 0.20.1 hosts Codex AI with multi-image references, Userfull Tools' long-image cutter and canvas clipboard export, shared language handling, size adaptation, feathering and timing. Launch with `start.cmd`; local legacy Userfull launchers now point to the same editor. No new package is produced for this merge; the published v0.4.0 ZIP predates the complete merge.

v0.4.0 integrates PhotoCraft 0.20.1 and multi-image references into the original Codex AI plugin. Both source and portable builds use 0.20.1; continue launching with `start.cmd`.

Multi-image references are now integrated into the original Codex AI plugin. Choose several images using the reference button, or drop them onto the AI toolbar; thumbnails are individually removable. Refer to them as “reference 1”, “reference 2”, etc. Continue launching with `start.cmd`; the separate Userfull Tools editor is not required.

v0.3.0 upgrades the matching editor to PhotoCraft 0.19.0 while retaining AI tools, direct image receipt, and editable mask feathering.

v0.3.1 fixes sharp feather boundaries with an inward fade to full transparency, and displays total elapsed time after successful generation. Adjust an existing layer's feather slider to apply the new mode.

Use **Edit selection, Remove object, and Generate image** directly inside PhotoCraft, from a native toolbar next to your selection. The integration uses your locally installed Codex CLI, its built-in image generation tool, and your existing sign-in. Results are imported as new layers with undo support.

### Download and start

1. Download **`photocraft-codex-ai-0.4.0-windows-x64-local-node.zip`** from the [v0.4.0 release](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.4.0).
2. Extract the entire archive into a writable folder. It includes the matching PhotoCraft editor, Python 3.13.5, and Pillow 11.3.0. **Node.js and Codex CLI are not bundled.**
3. Use your existing Node.js and npm-installed Codex CLI. If Codex is missing, run `npm.cmd install -g @openai/codex`.
4. Double-click **`start.cmd`**. Your existing Codex sign-in is reused; otherwise, follow the sign-in prompt for your own account.
5. Open an image in the newly launched editor, make a rectangular or lasso selection, enter a description, and choose an operation from the selection toolbar.

An internet connection and a Codex installation/account with working built-in image generation are required. GitHub's automatically generated **Source code** archives do not include the editor binary. The Windows x64 package is a preview development build: plugin 0.4.0 with a modified PhotoCraft 0.20.1 editor.

### Usage

| Operation | Behavior |
| --- | --- |
| Edit selection | Edit the selected area using your description; default feather: 12 px |
| Remove object | Remove the selected object and fill the background; no description required; default feather: 12 px |
| Generate image | Generate content inside the selection; default feather: 0 px |

Results are added as new layers, preserving the original. Press **Ctrl+Z** to undo. The toolbar is hidden when there is no selection; select the whole canvas for a full-image prompt. It follows the selection, zoom, pan, and rotation, moving above the selection near the bottom edge. Progress, cancellation, and errors appear in the toolbar.

**New in v0.2.9: editable mask feathering.** Right-click an AI result layer → **Edge feathering**. Choose the original selection, a centered circle, or a square, then adjust the **0–1000 px** slider or enter a value. The center comes from the layer's original pixel coverage; transparent results use their actual pixel bounds. New results have separate masks that can be adjusted without generating another image, support undo/redo, and persist in `.pcraft` files. Soft edges already baked into pixels by older versions cannot be reversed.

[Context menu example](examples/editable-mask-menu.png) · [Editable mask document](examples/editable-mask-demo.pcraft) · [Layered demo](examples/codex-ai-native-demo.pcraft)

### Proxy and local files

To use an explicit HTTP/mixed proxy, create `runtime/codex-proxy.json` inside the installation folder:

```json
{"url":"http://127.0.0.1:10808"}
```

`10808` is an example: replace it with your own proxy port and keep your proxy running. This setting applies only to Codex child processes launched by the plugin. It does not change system settings or global Codex configuration; local editor traffic bypasses the proxy. Delete the file to resume inheriting the existing network environment.

- Launch with `start.cmd` so both the editor and worker start. Do not launch only `native/photocraft.exe`.
- Editor settings are stored in `runtime/native-profile/`. Task images, prompts, results, and logs are stored in `runtime/native-jobs/`.
- Other PhotoCraft installations remain separate. Save your documents and close the old version before extracting an update. Update the matching editor through the plugin package to avoid replacing it with the upstream editor.

### Data handling and limitations

- Selection edits send **the full flattened source image and a reference image marking the selection** to Codex image generation. The selection limits local result compositing, not what is uploaded.
- The plugin uses the existing CLI sign-in without extracting login credentials and does not automatically fall back to a paid API. Cancellation stops the child process; a server-side job already in progress may still consume quota.
- The worker accepts token-authenticated localhost requests and rejects browser Origin requests. Codex runs with the `workspace-write` sandbox, `image_generation` enabled, and multi-agent mode disabled.
- Automatic import is refused if the document has changed or closed. A mismatched aspect ratio also prevents import while preserving the output; a different resolution with the same aspect ratio is scaled proportionally.
- Exported images and generated layers use 8-bit PNG. Professional fidelity for high-bit-depth documents and special color spaces has not been verified.
- Image generation availability depends on the Codex installation, account, model, and sandbox. Enabling the feature does not guarantee service access; failures are displayed and logs are retained.

### Source, fallback panel, and validation

See [native-source/README.md](native-source/README.md) for the Rust/egui patch and rebuild instructions. The bridge derives from OpenFill (Apache-2.0); component and license details are in [THIRD_PARTY.md](THIRD_PARTY.md).

The fallback Tk panel is mainly for source installations. It requires Python 3.10+ with Tk, Pillow, a desktop PhotoCraft installation, and a signed-in Codex CLI. Its source launcher is `start-panel.cmd`:

```powershell
pip install -r requirements.txt
python -m photocraft_ai --photocraft "D:/PhotoCraft/photocraft.exe"
```

The panel supports text-to-image, selection editing, and object removal, with a preview before applying results. Tasks are stored in `runtime/jobs/`. For the native Windows release, use `start.cmd`.

```powershell
python -m unittest discover -s tests -v
python -m photocraft_ai --connect-only
python tests/smoke_photocraft.py
```

See [VALIDATION.md](VALIDATION.md) for recorded results and known testing boundaries. These source-install commands require their dependencies and the matching editor; integration tests create test documents. Live image generation requires service access and consumes quota.

### Version history

| Version | Main change |
| --- | --- |
| [0.3.0](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.3.0) | Upgrade the matching editor to PhotoCraft 0.19.0, retaining all AI integration features |
| [0.2.9](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.9) | Editable layer masks; original selection/circle/square; 0–1000 px feathering |
| [0.2.8](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.8) | Receive complete PNGs directly from the current session; fix failed Windows copy commands preventing import |
| [0.2.7](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.7) | Use local Node.js and npm-installed Codex instead of bundling them |
| [0.2.6](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.6) | Legacy portable bundle including Python, Pillow, PhotoCraft, and Codex CLI |
| [0.2.5](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.5) | Remove extra feathering for image generation; preserve the original selection mask |
| 0.2.4–0.2.1 | Per-plugin proxy, HTTPS error classification and timeout, local edit feathering, single-generation and latency improvements |
