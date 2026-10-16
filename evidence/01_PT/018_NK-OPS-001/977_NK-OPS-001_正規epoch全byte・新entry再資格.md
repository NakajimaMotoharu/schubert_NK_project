# NK-OPS-001 正規epoch全byte・新entry再資格

2026-10-16、source7bb/PG3976/boot79a、SS343 SSC089/290、BUG1345/YKT1111。Production/SSは不変更。元4222/62769 actual1/payloadfc396はNKEPOCH1 magicを省いた前提でline290拒否、Root start予約/発行/native copy前。既4220/69058はliveでquiescentを観測、同stage/watchを再起動しない。

| Test ID | fixture/入力・独立期待値 | 実結果 |
|---|---|---|
| PT-OPS-EPOCH-FRESH-GOLDEN | SS089 literal NKEPOCH1＋7固定key/ASCII-LF/旧boot-run-cutoff-activation/INVALID digest -、独立permit SHA a×64 | 既独立former_issuedで全9行を検証。期待ISSUEDはgolden literalのstate/digest二fieldだけの差で、Production code未使用、純1成功 |
| PT-OPS-EPOCH-FRESH-NEGATIVE | magic欠落/未知、ISSUED混入、CRLF/LF欠落、誤key/cutoff/path traversal/Null | 全拒否、filename生成前に完全record/cohortを検証 |
| PT-OPS-EPOCH-FRESH-CLOSURE | 4234新only payload・正規UUID→固定dir permit O_NOFOLLOW/held fstatと全byte/hash/9metadata→同epoch hash/読戻し、Rootstart一箇所 | 全emitted静的0/純1成功。既sourceの盲目的prefix判定なし、Root/旧recordを書換えない |

新PG4236工具91/FES0・host/全emitted静的0、log SHAda96c6e52109e0e4cb83ad27209be41e21f2c2e8ea6a1f6a230362d0543e9544。command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg4236_canonical_fresh_qualification.py`。Production全3717/署名187/現配備を再実行0、Production PT加算0。

new entry **4f3cec2ed4a6be983a79f1f5cb21b25eb8b375173fc345b21ffa2cf68217cc06**、new-only `pg4234-canonical-fresh-noargs-once-v1`。watch50b30/managerac122他4artifactは既4230資格と同byte、実80read/1440値資格を流用でなく同一素材のまま参照する。設計mainff8b4f182の範囲内で上位仕様/期待値変更不要。actualnewRoot/新entry consumerは未実行、旧Root143を正常にしない。
