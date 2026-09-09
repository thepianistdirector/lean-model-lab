# Browser validation dependencies — phased review, 8 September 2026

**Current status:** the initial sandboxed shell smoke, first v1 workbench browser review, and tiny native 200% proof in full Chromium have completed. The actual final v2/14B workbench review remains pending. The dated phases below preserve their original proposals and receipts; see the final phase for current dependency and zoom evidence.

**Decision proposed for root review:** the three missing shared-library providers can be supplied from official AlmaLinux 8.10 RPMs in a project-local directory. Their remaining declared dependencies are already installed. This is a metadata-backed feasibility result, not a successful browser launch. No RPM payload was downloaded, extracted, installed, or loaded during this review; no system configuration changed.

The strict option for a shared VPS is a standalone CDP pipe harness with no listening port. The available `agent-browser` CLI introduces localhost listeners, so its normal daemon launch is not equivalent to private pipe transport.

## Observed local environment

- `/etc/os-release`: AlmaLinux 8.10 (Cerulean Leopard); architecture `x86_64`.
- Installed glibc: `2.28-251.el8_10.40`; RPM `4.14.3-32.el8_10`; DNF `4.7.0-21.el8_10.alma.1`; cpio `2.12-11.el8`. `rpm2cpio`, `gpg`, `gpgv`, `readelf`, `curl` and `sha256sum` are available.
- Existing headless browser: the existing host-cache entry `chromium_headless_shell-1193/chrome-linux/headless_shell`; SHA-256 `003728e0b77eb9d52e4d258594bd55ce22ecd245eb6d3b6858fbd844c901ad7d`.
- `ldd` on that existing binary reports exactly three unresolved names: `libatk-1.0.so.0`, `libatk-bridge-2.0.so.0`, `libatspi.so.0`. Every other entry resolves. The browser's own runtime version remains unverified until it can load.
- Node `v24.20.0`, Python `3.12.14`. Python Playwright, Selenium and Pyppeteer are absent. Project Node resolution finds no Playwright or Puppeteer.
- A cached native `agent-browser 0.36.0` executable runs `--version` and `--help` without installing anything: the existing cached package entry `agent-browser/bin/agent-browser-linux-x64`. SHA-256 `56d15181e51e00213f907fcf39707cfc76bfa804ff20f5a9373661c73f96de5e`. Package license: Apache-2.0. The cached musl variant is not executable; it was not modified or needed.

## Exact package graph

These are x86-64 AlmaLinux 8.10 AppStream packages, selected from the official repository's signed metadata, not packages for Ubuntu or a newer EL release. All three record the license as `LGPLv2+`.

| Required library | Exact RPM | Compressed bytes | Reported installed bytes |
| --- | --- | ---: | ---: |
| `libatk-1.0.so.0` | [atk-2.28.1-1.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/atk-2.28.1-1.el8.x86_64.rpm) | 277856 | 1294970 |
| `libatk-bridge-2.0.so.0` | [at-spi2-atk-2.26.2-1.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/at-spi2-atk-2.26.2-1.el8.x86_64.rpm) | 91612 | 318527 |
| `libatspi.so.0` | [at-spi2-core-2.28.0-1.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/at-spi2-core-2.28.0-1.el8.x86_64.rpm) | 173188 | 513975 |
| Total | Three RPMs | **542656** | **2127472** |

The reported installed total includes files beyond the selected libraries. The proposed extraction should include only the three library families, necessary symlinks, and their license notices.

Expected full-RPM SHA-256 values:

```text
882e6d686af8a7d3bd5080e43ba2a5cfab625b3384dcfcf25aa3971c4902ebf9  atk-2.28.1-1.el8.x86_64.rpm
ea0a4c413f9c23de510256d2c99ac870438bf8b95e6ba155ab9a134e672fdb85  at-spi2-atk-2.26.2-1.el8.x86_64.rpm
3f34083b191a471c62353d8a9e9cd262e16d8b624a2f4d7414a5f0326f4461f6  at-spi2-core-2.28.0-1.el8.x86_64.rpm
```

The graph is:

- `at-spi2-atk` requires `atk(x86-64) >= 2.25.2` and `at-spi2-core(x86-64) >= 2.25.3`; the proposed versions satisfy both. Its additional library requirements are glibc, pthread, GLib/GObject/GModule and D-Bus.
- `atk` requires GLib, GObject and glibc (`GLIBC_2.4`).
- `at-spi2-core` requires X11, Xtst, D-Bus, GIO, GLib, GObject and glibc (`GLIBC_2.7`), plus the D-Bus package. X11/Xtst bring their already-installed X extension dependencies.
- The RPM scriptlet requirements include `/sbin/ldconfig`; extraction does not execute scriptlets and does not run `ldconfig`.

Every remaining declared capability resolves through the installed RPM database:

| Capability family | Installed provider |
| --- | --- |
| glibc, pthread, GNU hash loader, `GLIBC_2.4`, `GLIBC_2.7`, `/sbin/ldconfig` | `glibc-2.28-251.el8_10.40.x86_64` |
| GLib, GObject, GModule, GIO | `glib2-2.56.4-177.el8_10.x86_64` |
| D-Bus ABI and `LIBDBUS_1_3` | `dbus-libs-1.12.8-28.el8_10.x86_64` |
| D-Bus package | `dbus-1.12.8-28.el8_10.x86_64` |
| X11 | `libX11-1.6.8-9.el8_10.x86_64` |
| Xtst | `libXtst-1.2.3-7.el8.x86_64` |

This closes the declared package graph. Actual `DT_NEEDED`, symbol resolution and browser startup still require inspection after root approves obtaining the payloads; metadata alone cannot prove those runtime results.

Corresponding source RPM names are `atk-2.28.1-1.el8.src.rpm`, `at-spi2-atk-2.26.2-1.el8.src.rpm`, and `at-spi2-core-2.28.0-1.el8.src.rpm`. Their official source location is `https://vault.almalinux.org/8.10/AppStream/Source/Packages/` (all three HEAD requests returned 200; source payloads were not downloaded). The live binary repository does not expose these source paths; its source URLs returned 404, so the official vault location is recorded separately. Keep each package's license files with extracted libraries. This review does not authorize redistribution or publication.

## Provenance and verification already performed

Local review metadata is under `.cache/browser-review/`; it contains no new browser libraries.

1. Retrieved [official AppStream repomd.xml](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/repodata/repomd.xml), SHA-256 `08736717473e58cf144d29a859a144f7cfb9c5135afc3e631c850010699e117d`, and its detached signature.
2. Downloaded the official [AlmaLinux 8 public key bundle](https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-8), SHA-256 `2cbe597b108cefbf571d8d430d238d0a7a6575eebf6c80649be5e10c323e7023`. The current fingerprint `BC5EDDCADF502C077F1582882AE81E8ACED7258B` matches [AlmaLinux's published 8.10 fingerprint](https://wiki.almalinux.org/release-notes/8.10.html). The same key ID is already present in the host RPM database; no key was imported there.
3. Imported public keys only into `.cache/browser-review/gnupg`. Verified the repository signature made `2026-09-08 09:56:11 UTC`: GPG returned `GOODSIG` and `VALIDSIG` for the current full fingerprint. The GPG web-of-trust status is undefined; key identity was checked against the official fingerprint rather than silently marking it trusted.
4. Verified compressed primary metadata SHA-256 `d156db6c7eaf6a156973b541ae7c121cdc74c1fdd8a7647af2559b2a80d242f1` and expanded XML SHA-256 `21e1970153cec4c36e659b9fafdc51e21e44778cd4fbba67a2235009a80a30cd`, both from the signed repository manifest. Retained the 3,930,850-byte compressed metadata as `primary.xml.gz`.
5. Retained the three exact package records in `packages.json`, the installed-capability checks in `installed-requirements.json`, and GPG output in `repository-signature.txt`. `metadata-manifest.json` records local metadata hashes.

The key bundle also contains the legacy, now-expired fingerprint `5E9B8F5617B5066CE92057C3488FCF7C3ABB34F8` and signing subkey `E53CF5EF91CEB0AD1812ECB851D6647EC21AD6EA`. Older RPMs may retain signatures from that era. Do not replace verification with `--nosignature` or global policy changes: the current-key signed repository metadata already binds each expected RPM hash, and the actual RPM signature must still be inspected after download.

## Proposed acquisition and extraction after root review

Do not run this phase until root accepts this concrete package graph.

1. Create project-owned mode-0700 `packages/`, `rpmdb/`, `stage/`, `run/`, `screenshots/` and `logs/` directories under `.cache/browser-review/`. Keep all shared caches and system configuration unchanged.
2. Download exactly the three pinned URLs into `packages/`, with HTTPS certificate verification, byte bounds and timeouts. Require their exact byte sizes and the hashes above. A changed repository or package requires renewed metadata reconciliation, not relaxed checks.
3. Initialize a separate RPM database at the absolute project `rpmdb/` path. Import the reviewed key bundle there only. Use `rpm --dbpath <project-rpmdb> --checksig --verbose <package>` and retain output; inspect each package's NEVRA, license, requirements, scripts, files and symlink targets using read-only RPM query options.
4. Before extraction, reject absolute archive paths, `..` components, special files, unexpected hardlinks and symlinks escaping `stage/`. Select only `usr/lib64/libatk-1.0.so.0*`, `usr/lib64/libatk-bridge-2.0.so.0*`, `usr/lib64/libatspi.so.0*`, their required in-tree symlinks, and `usr/share/licenses/...` records. Confirm actual archive names using `rpm2cpio` listing; do not assume a particular real-file version suffix.
5. Extract with `rpm2cpio` and cpio into the project stage, without RPM installation, scriptlets, `ldconfig`, root privileges, system D-Bus registration or service startup. Retain the original RPM bytes and a hash manifest of extracted files.
6. Inspect `readelf -d` and version requirements before any browser load. Set `LD_LIBRARY_PATH` to the absolute `stage/usr/lib64` path only in the owned browser subprocess environment. Re-run dependency resolution and a bounded browser `--version`; reject new missing symbols or changed core-library requirements.

## Automation choice and isolation

The cached CLI is usable without package installation, but source review of its [v0.36.0 Chromium launcher](https://github.com/vercel-labs/agent-browser/blob/eb05921bad874cd2a1b4fa5d1149f1ed26576cae/cli/src/native/cdp/chrome.rs) and [daemon](https://github.com/vercel-labs/agent-browser/blob/eb05921bad874cd2a1b4fa5d1149f1ed26576cae/cli/src/native/daemon.rs) found:

- It launches Chromium with `--remote-debugging-port=0` and uses a localhost CDP WebSocket.
- The daemon also starts a localhost streaming listener by default, even if no streaming command was requested.
- It automatically adds `--no-sandbox` in root/CI/container cases. This is a launcher decision, not proof that the browser sandbox cannot work.
- It supports `AGENT_BROWSER_SOCKET_DIR` for project-local Unix socket/PID/log files; `--config <project-json>` bypasses global config lookup. Its source commit is `eb05921bad874cd2a1b4fa5d1149f1ed26576cae`; that source provenance does not independently attest the cached binary's build.

**Root-selected shared-VPS option (payload review still required):** drive the existing browser directly over `--remote-debugging-pipe` from a small Node harness using only built-in modules. Child descriptors 3 and 4 carry NUL-delimited CDP JSON. Node `spawn` can allocate these with `stdio: ['ignore', 'pipe', 'pipe', 'pipe', 'pipe']`; no localhost HTTP/CDP server is necessary. This protocol transport still needs its actual startup test after payload review.

Use one unique, project-owned profile per run, an absolute project `--user-data-dir`, and process-scoped `TMPDIR`, `XDG_CACHE_HOME`, `XDG_CONFIG_HOME`, `XDG_RUNTIME_DIR`, and `LD_LIBRARY_PATH`. Do not change `HOME` or shared shell settings. Clear inherited browser/provider/proxy configuration in the child environment, retain no credentials, and point `Page.navigate` only at the generated standalone local `file://` artifact. Keep the page CSP active. No `--allow-file-access-from-files`, no `--ignore-certificate-errors`, no `--disable-web-security`, and no `--no-sandbox` are needed or approved by this review. Use normal headless/background-update suppression flags, not sandbox-disabling flags. Capture stdout/stderr and terminate only the owned browser tree on timeout or completion.

Root selected direct CDP pipe instead of the CLI launcher. For any future reconsideration of `agent-browser`, place its whole browser/daemon lifetime in a verified private network namespace before using it, preserve sandbox behavior with a reviewed launch guard, explicitly set project socket/config/profile paths, disable restore/state persistence, and close its owned session at the end. Merely binding to `127.0.0.1` does not isolate access from other VPS users. No namespace operation was performed in this metadata pass; namespace capability and sandbox feasibility remain unverified.

## Browser checks this would enable

After a successful, isolated launch, a pipe harness can use CDP [Page screenshot methods](https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-captureScreenshot), DOM/runtime observations, device metrics and keyboard input to check the actual artifact:

- Desktop and 320 CSS pixel viewport screenshots; inspect every saved image rather than relying on a file-exists check.
- Native Tab/Shift-Tab, Enter/Space and select-arrow interaction; record focus targets and bounding boxes, filter counts, empty state, reset and disclosure behavior.
- Console/runtime exceptions, expected labels, table structure, horizontal table scrolling and page overflow.
- Actual browser accessibility-tree snapshots. These do not establish a human screen-reader test.
- Text-size/reflow checks, keeping their exact mechanism explicit. Device pixel ratio, page-scale emulation and CSS `zoom` are different from a user selecting 200% or 400% browser zoom. Do not claim browser-zoom verification from those substitutes; retain that manual check if native zoom cannot be exercised in headless shell.

No screenshots, layout results, keyboard outcomes, browser zoom outcomes or accessibility-tree observations were produced during this feasibility review. Package and metadata checks cannot supply those missing observations.

## Root-accepted execution receipt — 8 September 2026

Root accepted the exact three-RPM graph for project-scoped, validation-only use. The initial metadata-only status above records the earlier phase; the following bounded actions have now completed.

- Downloaded exactly **542,656 bytes** across the three pinned RPMs. Every file matched its reviewed byte size and SHA-256. `acquisition-receipt.json` retains URLs, hashes and signature output.
- Verified each RPM using only the project RPM database. Header RSA/SHA-256 signature, package RSA/SHA-256 signature and payload SHA-256 all returned **OK** with legacy signing subkey ID `c21ad6ea`. The current-key signed repository metadata separately binds the exact complete-RPM SHA-256 values. No verification bypass was used.
- Inspected every newc archive member before extraction. Absolute/traversing names, special files, regular-file hardlinks and escaping symlinks were rejected. Selected only three real libraries, their three relative soname symlinks, and the three package license directories/files. No scripts, D-Bus services, plugins or unrelated package contents were extracted or run.
- Extracted real files are `libatk-1.0.so.0.22810.1`, `libatk-bridge-2.0.so.0.0.0`, and `libatspi.so.0.0.1`. Their hashes and selected payload records are in `extraction-receipt.json`; the full pre-extraction member inspection is `payload-inspection.json`. Readelf outputs are retained in `logs/`.
- With `LD_LIBRARY_PATH` set only for the owned subprocess to `stage/usr/lib64`, `ldd` resolved every dependency. No system library was replaced. `headless_shell --version` returned **Chromium 140.0.7339.186**, exit 0; see `version-receipt.json`.
- Executed `.cache/browser-review/cdp-pipe-smoke.mjs` using Node built-ins only. Its unique project profile/cache/config/data/runtime/tmp directories and clean child environment are recorded. The browser used `--remote-debugging-pipe`, with no TCP/HTTP server, no automation daemon, no external navigation and no sandbox-disabling launch argument.
- `Browser.getVersion` returned **HeadlessChrome/140.0.7339.186**, CDP protocol **1.3**, revision **`@c643dfff61ee0c447b89c05001216825c74120ff`**, V8 **14.0.1500365**. `Target.getTargets` showed only an `about:blank` page. No workbench or external site was loaded.
- A scan of socket descriptors owned by the browser process group found **zero TCP listening sockets**. `Browser.close` completed with exit code **0**. Final process-group inspection found **no remaining processes**, including zombies; no termination signal was needed.
- The initial renderer was observed with **`NoNewPrivs: 1`**, **`Seccomp: 2`**, and nested PID namespace identifiers. This supports that the browser's normal renderer sandbox started. Chromium's browser and some utility processes do not all use the same sandbox configuration; this is not a blanket security certification.

Exact retained stderr:

```text
[0908/140916.488787:WARNING:sandbox/policy/linux/sandbox_linux.cc:414] InitializeSandbox() called with multiple threads in process gpu-process.
```

The warning did not prevent the about:blank smoke from passing. Its implications for broader rendering remain unassessed; it was not suppressed. No `--no-sandbox`, global namespace setting, host security change, system installation, global environment edit, model job or publication occurred.

The machine-readable result is `.cache/browser-review/cdp-smoke-receipt.json`, with an immutable per-run copy at `.cache/browser-review/run/smoke-702c1f13-0435-4186-ad23-ac6f487e883d/receipt.json`. The only completed browser claim is the isolated, sandbox-enabled about:blank smoke. Actual workbench screenshots, narrow-layout, keyboard, filter, disclosure and zoom checks remain a subsequent task.

## Additional full-Chromium/native-zoom phase — 8 September 2026

Root reviewed and authorized this exact additional graph for project-local development QA only. It is not adoption into Lean Model Lab's runtime or release. The initial three-RPM receipts and their staged files remain unchanged. Only the additional ten reviewed RPMs were acquired; no new browser binary, package installer, global key/configuration change, service, or model workload was introduced.

### Exact acquired identities and signatures

The ten RPMs total **2,374,668 bytes**. Each matched its pinned byte count and complete-RPM SHA-256 and passed header/package signature and digest verification in the existing isolated project RPM database. Signature IDs `c21ad6ea` and `ced7258b` correspond to the reviewed legacy AlmaLinux signing subkey and current AlmaLinux OS 8 key described above. No signature or digest check was bypassed.

| Exact official RPM | Bytes | Metadata license | Verified signature key ID | Payload use |
| --- | ---: | --- | --- | --- |
| [avahi-libs-0.7-27.el8_10.1.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/BaseOS/x86_64/os/Packages/avahi-libs-0.7-27.el8_10.1.x86_64.rpm) | 62,712 | LGPLv2+ | ced7258b | Needed DSOs + notices staged |
| [cairo-1.15.12-6.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/cairo-1.15.12-6.el8.x86_64.rpm) | 734,828 | LGPLv2 or MPLv1.1 | c21ad6ea | Needed DSOs + notices staged |
| [cups-libs-2.2.6-68.el8_10.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/BaseOS/x86_64/os/Packages/cups-libs-2.2.6-68.el8_10.x86_64.rpm) | 448,008 | LGPLv2 and zlib | ced7258b | Needed DSOs + notices staged |
| [fribidi-1.0.4-9.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/fribidi-1.0.4-9.el8.x86_64.rpm) | 90,460 | LGPLv2+ and UCD | c21ad6ea | Needed DSOs + notices staged |
| [graphite2-1.3.10-10.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/graphite2-1.3.10-10.el8.x86_64.rpm) | 124,372 | (LGPLv2+ or GPLv2+ or MPL) and (Netscape or GPLv2+ or LGPLv2+) | c21ad6ea | Downloaded only |
| [harfbuzz-1.7.5-4.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/harfbuzz-1.7.5-4.el8.x86_64.rpm) | 301,740 | MIT | ced7258b | Downloaded only |
| [libXft-2.3.3-1.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/libXft-2.3.3-1.el8.x86_64.rpm) | 67,900 | MIT | c21ad6ea | Downloaded only |
| [libdatrie-0.2.9-7.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/libdatrie-0.2.9-7.el8.x86_64.rpm) | 33,696 | LGPLv2+ | c21ad6ea | Needed DSOs + notices staged |
| [libthai-0.1.27-2.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/libthai-0.1.27-2.el8.x86_64.rpm) | 207,524 | LGPLv2+ | c21ad6ea | Needed DSOs + notices staged |
| [pango-1.42.4-8.el8.x86_64.rpm](https://repo.almalinux.org/almalinux/8.10/AppStream/x86_64/os/Packages/pango-1.42.4-8.el8.x86_64.rpm) | 303,428 | LGPLv2+ | c21ad6ea | Needed DSOs + notices staged |

```text
22c7386ab6b731641b22371abdacc6867617b001e40fdc7677fb4f2c7b11e2fe  avahi-libs-0.7-27.el8_10.1.x86_64.rpm
68bc20d9d2959635aa877f588e9cd3fb44562976fcdb2c6c4057620cbe78a81d  cairo-1.15.12-6.el8.x86_64.rpm
569a95c3f900b08c9a98d288ef2f1de4efeacbc267ed5a792ad9c826b6e0c540  cups-libs-2.2.6-68.el8_10.x86_64.rpm
c4e39bfb5d2189b21e6785e79e213e3f5cf42e44a868cc55e741c7f8a75ba7d2  fribidi-1.0.4-9.el8.x86_64.rpm
4ea7d9a9c186f0643c2df8f060a3c085261a12f812ad8e062944847752f5f618  graphite2-1.3.10-10.el8.x86_64.rpm
61a039f3de406bc5ca3a761bcbc36c4724832a209c45187d25568c872225a59a  harfbuzz-1.7.5-4.el8.x86_64.rpm
c80023863bd41be320866f2ca4377694a52ed508f27afdebd1d4fb6dcc956b36  libXft-2.3.3-1.el8.x86_64.rpm
11365d789d47e43b27cc08a4a8cc24024589fde0f64ae9a60987107060130a19  libdatrie-0.2.9-7.el8.x86_64.rpm
e878dc3b251e1b171945b8b4ea1363cede36e2d50aff6be47a1f796c31c5d3f4  libthai-0.1.27-2.el8.x86_64.rpm
382505d5d7c00fcd919eab817c0d2d7af21c6492282d85498cd1d3a4a35d54c2  pango-1.42.4-8.el8.x86_64.rpm
```

AppStream reused the previously verified content-addressed primary metadata. BaseOS primary metadata matched SHA-256 `937e40aa5372742c98f02766cd350da5b6c6a5375dbe07ddf40698595c83f731`; its parent repomd signature verified with fingerprint `BC5EDDCADF502C077F1582882AE81E8ACED7258B`. The BaseOS compressed metadata is 60,337,267 bytes. Detailed metadata/provider records and actual signature output are retained locally as `.cache/browser-review/native-zoom-plan.json` and `.cache/browser-review/native-zoom-acquisition-receipt.json`; they are not distributed in the source archive. Their hashes and verified scope are recorded in the included [native-zoom evidence summary](../evidence/browser-0.4-native-zoom.json).

### Narrow extraction and notices

All payload members, scripts, ELF dynamic requirements and embedded license files were inspected without executing package code. The observed script hooks were ldconfig hooks in libthai, libdatrie, HarfBuzz and Pango; none ran. Recursive ELF inspection covered 87 existing/proposed objects and resolved all required names without new dependencies. It established a narrower load set than the aggregate RPM dependency graph: **eight additional real DSOs from seven packages**, seven SONAME symlinks and nine notice files, **24 staged files total**.

The staged SONAMEs are `libcups.so.2`, `libcairo.so.2`, `libpango-1.0.so.0`, `libavahi-client.so.3`, `libavahi-common.so.3`, `libfribidi.so.0`, `libthai.so.0` and `libdatrie.so.1`. HarfBuzz, Graphite2 and libXft remain downloaded but unextracted; only unused sibling Pango libraries needed them. No Cairo/Pango/CUPS helper executables, plugins, services or unrelated data were extracted. The selected files live under project cache `native-zoom-stage/`; detailed file records and payload inventory remain locally as `.cache/browser-review/native-zoom-extraction-receipt.json` and `.cache/browser-review/native-zoom-payload-inspection.json`, not distributed in the source archive. The included [evidence summary](../evidence/browser-0.4-native-zoom.json) records the receipt hashes, selected SONAMEs and verification limits.

Preserved notice paths within the native-zoom stage:

- `usr/share/licenses/avahi-libs/LICENSE`
- `usr/share/licenses/cairo/COPYING`
- `usr/share/licenses/cairo/COPYING-LGPL-2.1`
- `usr/share/licenses/cairo/COPYING-MPL-1.1`
- `usr/share/licenses/cups-libs/LICENSE.txt`
- `usr/share/licenses/fribidi/COPYING`
- `usr/share/licenses/libdatrie/COPYING`
- `usr/share/doc/libthai/COPYING`
- `usr/share/licenses/pango/COPYING`

Metadata license expressions and embedded notices are both retained. This development validation does not authorize binary redistribution; the staged libraries are not release dependencies.

### Startup correction, transport and scoped network evidence

The existing full Chromium `--version` returned **140.0.7339.186**, exit 0; browser SHA-256 is `5386de944dc312f838d69a974253d23bdb029acc072e28e6b11aa478c8b504d5`. An initial SIGTRAP was diagnosed from the owned minidump, existing binary symbols/disassembly and pinned Chromium source: the temporary singleton socket path was 193 bytes, exceeding its 107-byte non-NUL limit. Root authorized a fresh mode-0700 `.tX` directly under the project as child-only TMPDIR. Actual socket paths became 105 bytes; the long profile/receipt paths remained unchanged. Owned short directories were removed only after complete browser closure. No writes went outside the project.

The harness uses Node built-ins and CDP pipes, without a TCP server or sandbox-disabling launch flags. Full Chrome rewrites `/proc` command strings, so renderer detection was corrected to split whitespace; the original falsely failing receipt remains intact with an [included false-negative adjudication](../evidence/browser-0.4-native-zoom.json). The standard renderer observations were `NoNewPrivs=1` and `Seccomp=2`. The GPU-process multithread sandbox-initialization warning remains in the logs and does not imply all browser processes share renderer sandbox properties.

Full Chromium attempted background Google URLs despite `--disable-background-networking`. Root authorized only the additional process-local `--host-resolver-rules=MAP * ~NOTFOUND` single argument and a private project `--log-net-log` path. Seven hostname-resolution completions returned `ERR_NAME_NOT_RESOLVED` (-105) in each tiny proof. Netlogs remain mode 0600 inside mode-0700 per-run directories.

A recorded UDP connect to the literal IPv6 probe address was reviewed rather than silently ignored. Exact Chromium 140 code and linked netlog sources established a local route/address probe: `SOCK_DGRAM` → `connect()` → `getsockname()` → close, with no send/write or remote handshake. The final gate permits only that exact source-linked, closed probe with the expected address/local-address events, and stops for send events, TCP events or unmatched connections. Both proof traces had no UDP bytes-sent/TCP-connect events, and owned IP socket/TCP listener snapshots were empty. These are bounded observations, **not universal egress isolation or a claim of zero attempted browser requests**. The initial STOP receipt remains unchanged with its [included source/trace adjudication](../evidence/browser-0.4-native-zoom.json).

### Native zoom result and remaining artifact gate

The same tiny local data document and 1440×1000 outer window were observed with native `cssVisualViewport.zoom` **1 → 2**, CSS viewport width **1440 → 720**, DPR **1 → 2**, visual viewport scale **1 → 1**, and unchanged CSS probe dimensions **100×44** and CSS zoom **1**. Both screenshots were visually inspected. The native profile preference path is `partition.default_zoom_level.x`, set to `log(2)/log(1.2)` for the 200% profile; no CSS, font-size or device-scale override supplied this result.

Both runs closed with exit 0, no remaining owned processes, and owned short-temp cleanup. The final zoomed run returned PASS under the narrow reviewed network rule. The included [native metrics and evidence hashes](../evidence/browser-0.4-native-zoom.json) preserve the comparison, binary/harness/receipt/netlog/capture identities, sandbox/cleanup/network scopes and original false-negative adjudications. Full captures, harnesses and raw receipts/netlogs remain in local `.cache/browser-review/` and are not distributed in the source archive.

The native mechanism and local route probe are traceable to the pinned [zoom preference implementation](https://chromium.googlesource.com/chromium/src/+/140.0.7339.186/chrome/browser/ui/zoom/chrome_zoom_level_prefs.cc), [native zoom readback](https://chromium.googlesource.com/chromium/src/+/140.0.7339.186/third_party/blink/renderer/core/inspector/inspector_page_agent.cc#1675), and [resolver probe implementation](https://chromium.googlesource.com/chromium/src/+/140.0.7339.186/net/dns/host_resolver_manager.cc#1534).

Separately, the earlier real v1 comparison/recovery workbench was exercised at desktop and 375px with seven filters, disclosures, cost history, empty/reset states and retained missing observations; see [current workbench review](../review/workbench-accessibility.md). Its 200% CSS content-enlargement check is explicitly separate from this tiny native-browser proof. **The actual final v2/14B HTML still requires its own native200 layout and interaction review after root hands it off between inference studies.** No large workbench was opened during the tiny zoom proof. No broad accessibility or browser-security certification is claimed.
