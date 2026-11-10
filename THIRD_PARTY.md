# Third-party code

The files under `vendor/openfill/` and `vendor/openfill_photocraft/` originate from
Beckett Harriman's OpenFill, Apache-2.0:
https://github.com/beckettharriman/openfill

Upstream commit: `84f904dca2d1eaf6b506b3b8a7043e3ea116e482`.
License: [vendor/OPENFILL-LICENSE](vendor/OPENFILL-LICENSE).
Copyright and SPDX headers are preserved. Local transport modifications are documented in that file.

Version 0.2.7 expects a locally installed Node.js/Codex CLI and does not redistribute them.
The legacy 0.2.6 Windows x64 portable
bundle additionally includes Codex CLI 0.166.0 (Apache-2.0), its command/sandbox helpers,
and ripgrep. Their license texts are included under `tools/codex/`.
Codex upstream: https://github.com/openai/codex/tree/rust-v0.166.0
Ripgrep upstream: https://github.com/BurntSushi/ripgrep (MIT OR Unlicense).

The portable bundle includes the official CPython 3.13.5 Windows embeddable runtime
(PSF license, `python/LICENSE.txt`) and the official Pillow 11.3.0 Windows wheel.
Pillow and its binary dependency license notices are preserved under
`python/Lib/site-packages/pillow-11.3.0.dist-info/licenses/`.
Python source/distribution: https://www.python.org/downloads/release/python-3135/
Pillow source: https://github.com/python-pillow/Pillow/tree/11.3.0

The current development build also uses NumPy 2.2.6 (BSD-3-Clause) and
opencv-python-headless 4.12.0.88 (OpenCV Apache-2.0 and wheel-specific notices)
for selection-context alignment. Their Windows wheels, including bundled binary
dependencies and license notices, are preserved under `python/Lib/site-packages/`
(`numpy-2.2.6.dist-info/`, `opencv_python_headless-4.12.0.88.dist-info/`, and `cv2/`).
Source installs obtain these packages through `requirements.txt`; offline portable
builds extract their pinned wheels alongside Pillow, with no download at launch.
Sources: https://github.com/numpy/numpy/tree/v2.2.6 and
https://github.com/opencv/opencv-python.

## Native editor integration (0.2)

The optional `native/photocraft.exe` is a locally rebuilt PhotoCraft 0.20.1, based on
https://github.com/storytold/photocraft at `327c4cc82e737a3e0af7c147a477126d77525495`.
PhotoCraft is MIT OR Apache-2.0; its LICENSE-MIT, LICENSE-APACHE, NOTICE and ATTRIBUTION.md
are preserved alongside the binary. The local source patch is in `native-source/`.

Reference-image attachments are adapted from the user's PhotoCraft Userfull Tools
repository, https://github.com/kaliwell/photocraft-userfull-tools,
commit `c05124bca29def76e35b2293245161c34da75eba`, and integrated into the 0.20.1 editor.

The unified development build also adapts Userfull Tools v0.3.8's native cutter,
clipboard export and language helpers, and its v0.3.7 image-size adaptation with
reference support. These are hosted in the same PhotoCraft process.
