# Third-party code

The files under `vendor/openfill/` and `vendor/openfill_photocraft/` originate from
Beckett Harriman's OpenFill, Apache-2.0:
https://github.com/beckettharriman/openfill

Upstream commit: `84f904dca2d1eaf6b506b3b8a7043e3ea116e482`.
License: [vendor/OPENFILL-LICENSE](vendor/OPENFILL-LICENSE).
Copyright and SPDX headers are preserved. Local transport modifications are documented in that file.

Codex is a separately installed application and is not redistributed here.

## Native editor integration (0.2)

The optional `native/photocraft.exe` is a locally rebuilt PhotoCraft 0.18.0, based on
https://github.com/storytold/photocraft at `422ca7beda90d927643bcd074646ebbd37706d75`.
PhotoCraft is MIT OR Apache-2.0; its LICENSE-MIT, LICENSE-APACHE, NOTICE and ATTRIBUTION.md
are preserved alongside the binary. The local source patch is in `native-source/`.
