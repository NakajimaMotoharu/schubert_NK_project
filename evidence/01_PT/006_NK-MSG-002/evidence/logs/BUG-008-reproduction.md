# BUG-008 修正前再現

- 発見日: 2026-09-04
- 対象commit: `dcc90fe`
- 期待: SS 352 §11.2の`NKENC1` magic/format/key ID/nonce/ciphertext/tag envelopeとlength-prefixed AAD
- 実際: `nonce || ciphertext || tag`だけを保存し、固定vectorはexpected 68 byteに対しactual 58 byte。独立`NKENC1` previous-key vectorの復号もtag不一致となった
- 実行結果: `ResponseSnapshotCodecTest` 6件、failure 1、error 1、skipped 0
- 原因: Program固有SS 324を実装する際、全AES共通のSS 352 §11.2/SS-D-045を同じvectorへ統合しなかった
- 修正: commit `50d0a91`で`NKENC1` envelope、別列key version一致、format/key ID/AAD検証を実装
- 再試験: Run `PT-IDEM-20260904-01`で関連6 JUnit methodと全分岐をPASS

Raw ciphertext、nonce、keyは保存していない。
