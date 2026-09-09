# GCC 8 build compatibility review

Decision date: 2026-09-08. The owner explicitly approved the pinned llama.cpp
v0.2.0 source, official Qwen FP16 model and original two-hour CPU allocation.
Acquisition succeeded, including the exact model SHA-256. This review records
the necessary local compiler compatibility changes before any inference.
It adds no package, compiler, remote code, model, precision or policy.

The first build failed linking the build-time UI embedding helper. GCC 8.5
requires its separately shipped `libstdc++fs.a` for C++17 filesystem support.
The existing compiler installation contains that archive. Setting
`CMAKE_CXX_STANDARD_LIBRARIES=-lstdc++fs` resolved those symbols without source
changes or machine-wide installation. The build-time helper is still needed
to produce the disabled-UI stub; UI/network asset acquisition stays disabled.
[GCC 8.5 library manual](https://gcc.gnu.org/onlinedocs/gcc-8.5.0/libstdc%2B%2B/manual/manual/using.html).

The next build reached `server-schema.cpp` and failed on numeric-field
constructor template deduction in new-expressions, consistent with the
[documented GCC bug 85883](https://gcc.gnu.org/pipermail/gcc-bugs/2019-January/647520.html).
No newer compiler was found in the existing toolchain locations inspected.

## Exact patch and semantics

Upstream remains commit `bb4caa7540188872173c44d161602d9271386413`.
The additional patch is `patches/llama-cpp-v0.2.0-gcc8-ctad.patch`, SHA-256
`598d10a911e4d9c33926bd2dfd75735d143b84db14ad644a7502f35bec8e0f1c`.
This is explicitly a patched local build of that source, not an unmodified
upstream binary. Both comparison arms use the same exact resulting binary.

All 41 edits replace `new field_num("key", params.member)` with
`new field_num<decltype(params.member)>("key", params.member)`. Six are inside
an existing disabled `#if 0` block. The original constructor deduces `T` from
`T &`; the unparenthesized member-access `decltype` selects the same declared
scalar type. Integer widths/sign, floating-point parameters, reference
binding, limits, JSON conversion, clamping and exception behavior are unchanged.
The patch adds no executable logic or inference arithmetic.

A fresh-context, read-only GPT-6 Astra review reported no findings in this exact
patch. The root's GCC 8 test confirmed type equivalence to stack-constructor
deduction, common reference binding and numeric limits for signed 32/64-bit
integers, unsigned 32-bit seed, float and double. These are scoped compatibility
checks; actual backend build and runtime results remain separate evidence.

The package carries the patch and upstream MIT notice. Setup receipts and the
frozen comparison configuration bind the patch digest in addition to the base
commit and binary SHA-256. A changed or absent patch identity fails validation.
Fresh setup applies the checked patch before compiling. It is applied uniformly
on supported reproductions, so compiler version cannot silently select a
different backend source recipe.

## Recovery and allocation

Both failed builds remain in the acquisition/build journal. Recovery uses the
original acquisition start and deadline, retained downloaded model/source and
the same output tree, with fresh logs/receipts. It does not acquire another
model, reset the allocation or erase failed build costs. The setup failure
revealed a missing standalone boot/allocation sidecar; fresh preparation now
writes one before acquisition. This initial run retains an explicit same-host,
same-boot reconciliation observation instead of pretending that sidecar existed.

Rollback means reverting the project recipe/configuration and patch before a
new registered comparison, while preserving the failed-build and measured
evidence. Any new dependency, compiler acquisition, model change or increased
resource allocation still requires the corresponding exact decision.
