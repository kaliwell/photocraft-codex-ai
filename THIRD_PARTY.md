# Third-party code

The files under `vendor/openfill/` and `vendor/openfill_photocraft/` originate from
Beckett Harriman's OpenFill, Apache-2.0:
https://github.com/beckettharriman/openfill

Upstream commit: `84f904dca2d1eaf6b506b3b8a7043e3ea116e482`.
License: [vendor/OPENFILL-LICENSE](vendor/OPENFILL-LICENSE).
Copyright and SPDX headers are preserved. Local transport modifications are documented in that file.

The source bundle expects a separately installed Codex CLI. The Windows x64 portable
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

## Native editor integration (0.2)

The optional `native/photocraft.exe` is a locally rebuilt PhotoCraft 0.18.0, based on
https://github.com/storytold/photocraft at `422ca7beda90d927643bcd074646ebbd37706d75`.
PhotoCraft is MIT OR Apache-2.0; its LICENSE-MIT, LICENSE-APACHE, NOTICE and ATTRIBUTION.md
are preserved alongside the binary. The local source patch is in `native-source/`.
