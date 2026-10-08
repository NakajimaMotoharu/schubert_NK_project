# PG556 真正親完了独立receipt仕様

NK-BAT/OPS、SS343/SSC190218、451、WBS-N15.04依存。PT-OPS-PG556-DONE001: 同current source969/PG548、実親581443/Invocation075ad6644b284056a6cccf7af252519b、PID1start job59402/startMono44878901762、実新run b7e73994-b951-4696-bdd1-cfbc8a10e734/cutoff2026-10-08T04:03:00.714124Z/activation12f1af04-180e-405c-8738-853bbd875443。

独立oracleはPID1 journal boot/pid1/uid0/COMMsystemd/unit/Invocation、uniquecursor、start..1800秒内、jobstart/doneとUnitSucceeded各一件を要求。NKDONE1 exact六行/140..141byte/固定run-cutoff-activation/outcome0、終了時刻はcutoff以後/PID1完了以前60秒以内に合同。旧完了の再利用・GC counters0・APIready単独・途中rowは成功根拠でない。期待はliteral記録構造/既承認PID1contractから独立作成、Production methodで生成0。

2管理test: literal正常60秒、全fieldmissing/foreign/null、任意非空cursor許可と空拒否、duplicate/missingreceipts、badmagic/outcome10/foreignrun、隣接timeout境界。初回TDDのcursorに任意foreign非空を拒否すべきというfixture誤りを空cursor拒否へ是正（仕様ではcursorは任意unique非空、未実装TDDにつきBUGでない）。Pyflakes0、Production PT加点0。真正実receiptは未取得、native/正式・IT/STは未受入。
