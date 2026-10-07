# PG530 依存集合全terminalfresh正常scope再試験

Productiona2/PG495/schema028、SS343353/SSC215・QA047/BUG825YKT594。PG529限定回収actual0・全原値二読/自peer-lock0/新Ref正常返却後の別fresh連続M→A→RODB/advisory→十Ref/FD→原本→各正常close。旧PG528 actual143/UNKNOWN/refs-only、元PG526四STOP/原本SUCCESS/ISSUED7/全24-462/native8を維持。

| Test ID | 独立期待値と根拠 | command |
|---|---|---|
| PG530-H01 | 当親PID1/boot/DONE/1800s・旧452保持+10SKIP/attempt literal80assert、null/未知Javaarg6/NPE0/Werror0 | pg530_terminal_compile_v1.sh |
| PG530-H02 | 共通typed dependency_graph の10Unit/5prop/empty/reorder/missing/duplicate/foreign/token/null/上限888assert、stdin定義/source一致 | pg529_dependency_graph_test.py |
| PG530-V00 | 同helperSHA d48c2d26…/graphSHA5931ef96…、全10Unit読取Refを保持した実snapshot二読/全currentUnit18/宣言/依存集合/親DONE/三stopjob/全24-462/原本Backup/startup7/native8/原error・旧18file/runtime、不変/peer-lock0。診断はJava ownerを取得せずscope受入0・業務操作0 | pg530_terminal_snapshot_probe_v3.py actual0/log775ba091… |
| PG530-V01 | V00と同sourceにfrozen class2/helper1/graph1を結合して、実通常Java新M-A/RODB/advisory/十Ref/FDの全scope正常。current dependencies rawは別before/after fileで保全、logical集合だけを比較 | pg530_terminal_native_v1.py |

V00 prototype履歴: v1は診断で十Refを持たずgraphの参照側Unitが未materialize、graph集合guard拒否actual1/log23428451…（SAVE/Java/業務操作0）。実nativeの十Ref条件をdiagnosticにも明示してv2 actual0としたが表示run labelは旧v1誤記のため正式joinへ使用しない。v3は一意run label/exit/source/logの結合を実施、actual0をnative前にhash/source必須照合する。新しいnative成功や正式sourceへprototype結果を読み替えない。原失敗source/logは別保存。

実行: `bash tools/quality/vm/050_s1/pg530_terminal_compile_v1.sh`（new-only）、V00 v3後source固定し `python3 -B tools/quality/vm/050_s1/pg530_terminal_native_v1.py` 一回。四STOP/起動/配備/runtime操作/DBwrite0。旧success/UNKNOWNを混ぜず、新DB→Ref/bus/FD→A→M全正常/独立自peer-lock0を結果へ付ける。native8存在は100%ではない、未起動Inspector/Bootstrapを合格へ加算0。raw DB/token/session等は私有、Gitはsafe manifest/hashのみ。native/全quality/正式は実結果で更新する。

実結果: source7febbe509、native78246 actual0/5.818508259s/logc6de98aa…、Root before=afterd08b56b1…/complete351201a9…/rawdependencies before=after766a994f…。全10Unit18/currentkernel終端、当親真正DONE/原本SUCCESS/全24-462/旧452+10承認SKIP・原本Backup/startup7/native8/runtime/旧18fileの前後二読一致、新DB/Ref/bus/FD/A/M全正常と独立peer/advisory/FLOCK0を確認。safe=evidence/provisional/PG530-terminal-readback-v1/manifest.json。旧UNKNOWN/143は保全、単一freshscope正常を全native/正式認定へ代用0。
