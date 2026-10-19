# protocol27通常PT・静的ABI結果

2026-10-20、仕様1183、BUG1476/YKT1237。Production Main/Test source **d77712899fca49f80bef4a6356e96e9bb90b149f**。PG5728元exec62644 actual0、開始2026-10-19T22:40:57.703589Z/終了22:41:18.405692Z、phase0/0、archive **4b1a06d3c2cd9a21dd35a877ab9754889954d06e8c4be2fa75144f376bea0952**。

通常実行PT **88/18suite、FES/flaky/rerun/not-run0**、source固定/全inventory一致/型null・SpotBugs0。実四counter LINE3468/3468、METHOD741/741、CLASS157/157、BRANCH1010/1010、物理Main174、追加除外0。coverage XML **2109ab4d4c65147283608453841c9239e9d6e5a5c356a181be0bbea01f6e03a7**。新規TestID加算0（既ENUM002対象を23型に拡張）、旧source成功の転用0、拒否PT代替0。

PG5729-v1元22735 actual1はBUG1477/YKT1239：javap CP番号の桁による表示空白一字で誤拒否。元失敗を保全し、a9251299dでCP参照直後のcomment paddingだけ正規化した。固定工具unittest3成功、opcode/literal/公開method/branch先変異を非同義として保持。通常PTは再実行せず、同d777 source/実byteを新v2元64351 actual0で静的照合した。

全23型/27field厳密private-only sourceモデル、全公開ABI/opcode同義、全849Main/実aux1664（当protocol174＋source不変の他1490、fresh全体compileとの主張無し）。PMD7.28.0 exit4/raw**1620**/処理error0、Checkstyle14.3.0 exit0/指摘0、当27命名警告0。先行1629から九減、元1647から二十七減。F03全体は未受入、YKT1237は残enum21＋serialized Throwable16=37でOPEN。

公開元結果：`evidence/provisional/PG5730-protocol88-enum27/manifest.json` SHA256 **85000de6489bf89fc93630fc610d8324eb09c0eb98d159e72e076772d5d1f4e1**（実XML全88TestID/hash、環境/command/exit/coverage）。別静的 `evidence/provisional/PG5729-protocol27-static-v2/manifest.json` SHA256 **6587f9f792bf82c0953f06ec56789777089560ec9b9184e05d0763b0b328d828**、全findingも同directory。私有raw/source snapshotはwork/pgpt-runs/PG379の各new-only runへ保全。

BUG1476は当protocol九scopeCLOSED、BUG1477/YKT1239は当表示正規化工具scopeCLOSED（2026-10-20）。新全体/native/CHR/実所有/QA051final/451正式は未受入。正式1964PT/53scope・工数null維持。次は残enum21を独立PG/PTとして分解し、既保留の失敗cohort/intent/permit/VM操作へ進まない。
