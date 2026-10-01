# NK-OPS-001 Root起動世代接続 実行結果

2026-10-01開始。SSC137/PT297先行、正式認定run24/1964PT/53scope/48.3%は据置。正規issuerのPG405証拠は296を参照し、新S3Sourceへ流用しない。Root/native/全業務ready/CHR/coverage100%は未実施・未受入。

## 暫定選択検証（PG406、未commit Source）

凍結Source `dc81ba72039f0c88b4a68779095b8a4408f0018a` の最初の全6はexit1（16:32:36/5分51秒、log SHA256 `f1d102dadffbce9480f377a049369f22d5bb7f31ae81e065d7100d6d210fd812`）。API754PT中2F・E/S0、Web/Batch未実行、BUG401/YKT321を修正前登録。API内の旧Unit oracleのみSS342/SSC137139へ整合、普通MainのFixedServiceExecArguments oracleは保持。限定v1/v2はProtocolに指定test無しで試験開始前拒否、合格0・Work保存。v3は各moduleで実在testを指定し全5module/static各0/exit0（16:37:17/50.335秒）、ApplicationServiceUnitTest4/RootServiceUnitTest2/FixedServiceExecArgumentsTest4/LinuxInodeSecurityTest9とProtocolを確認。全6再回帰/nativeは未実行。Production codeはdc81ba720から不変更。

2026-10-01 16:12 JST: s3-selected-v5 全89PT（Storage9/Bootstrap4/Batch76）F/E/S0、SpotBugs3module 0、44.602秒/exit0。ログSHA256 `5ee5d6a8daf23b24583078392797bbb3b5a225b76cee3b145698d503ce90b14e`。当回epoch.current/intent namespace・Root proof/ELF/A観測・親API/WEB観測FD close-onlyを確認。v4全87PT/FES0/static3zero（16:01:51/41.896秒、SHA256 `4d7e09ddfb7b00a7578139afe7fbbec770761d268cc7cf59761d2b39d27e4d14`）もWork保全。BUG399/400・YKT319/320の直接範囲は成功、全6/実native/100%の横展開閉鎖は未実行。

SSC141/ROOTDEPLOY001: 固定旧commit485e3daのAPI/Webテンプレート→候補Rootテンプレートと、独立最小literal/11種負変更/未知Unitを検証、全27assertion成功・VM書込0。工具javac `-Xlint:all -Werror`成功（compile-only annotation classpath不足による初回28warning/exit1をWork保全し、既存annotationsを明示後に再試験、警告抑制追加0）。Sourceの正式PT件数には工具27assertionを加算しない。

root-inputs v5: 不要wrapper注釈除去後の全43PT（16/4/23）F/E/S0、SpotBugs3module 0、15:20:45/41.383秒/exit0。s3-selected-v1: 新実exec/親起動を含む全78PT（9/4/65）F/E/S0、Batch静的3指摘でexit1（BUG395/YKT315同原因）。Root生成・原本・DB/Ops/held ELF・実FD/権限移行のnativeはまだ未実行、合格へ流用しない。

- launch v4: Storage/Bootstrap/Batch全82PT F/E/S0、SpotBugs3module 0。v1/v2 compile失敗・v3 static失敗もWorkに保全、合格へ混入しない。
- root-inputs v2/v3: 全143PT中各1F、BUG397/YKT317。v2は借用buffer故障後のfixture消去責務欠落、v3はremaining=1限定EOF faultの未注入。Production expected不変更。
- root-inputs v4: 共用fixture利用全classを追加して全217PT（16/22/179）、F/E/S0、2026-10-01 15時台。SpotBugsはBatch不要抑制1件（BUG395/YKT315同型）でexit1、run全体は未合格。全6/native/100%は未実施。
- Work logs: `/home/mini/codex/project1/work/pgpt-runs/PG379/pg406-launch-selected-v1.log`～v4、`pg406-root-inputs-selected-v1.log`～v4。Sourceがdirtyの選択検証であり正式same-source manifestは未発行。
