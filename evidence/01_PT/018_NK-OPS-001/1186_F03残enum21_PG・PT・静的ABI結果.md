# F03残enum21 PG・PT・静的ABI結果

2026-10-20、1185/BUG1478/YKT1237。PG実装fe8a208a4、実検証source **a718e3a2f0c948c6016986b16917c22d39471dfa**（Main/Testはfe8aと同byte、工具だけBUG1479是正）。PG5732-v2元90313 actual0、22:49:15.598143Z→22:51:24.526419Z、archive **2c508820c3eadcb74ae106fa72b70a6991f0af699dd794d3810940b8807dd773**、phase0/0/source固定。

通常実行**12PT/7suite、全XML一意・FES/flaky/rerun0**。新五値catalog caseと必要依存golden3/Range4、旧成功の合算無し。六module全1664Mainを当sourceでcompile、型null/SpotBugs六module各0。対象14enumの実LINE182/182・METHOD62/62・CLASS14/14・BRANCH14/14、全counter miss0（branch無し型は0/0と記録、除外追加0）。module全体coverage100は主張しない。実個別counterは公開元manifestを正とする。

PG5734元59815 actual0：元6dbからの37file/48private fieldを厳密モデル・全37enum公開ABI/opcode同義で照合し、外側業務処理は不変更。全849Main/当六compile1664auxでPMD7.28.0 exit4/raw**1599**/処理error0、Checkstyle14.3.0 exit0/指摘0。当48同名field警告0、残はserialized Throwable16。今回21除去、先行protocol含め計48除去。YKT1237全64中48是正だが残16/全F03未受入。

公開 `evidence/provisional/PG5736-enum48-catalog12/manifest.json` SHA256 **1ce0dc4201b07559fa10824481ad8f6d80f285c0288182840b3f333c268bada4**、全12XML/TestID/hash/command/環境/coverage hash/対象counter/五fixture hashを保持。別静的は001_NK-PRO-001/evidence/provisional/PG5734-enum48-static-v1/manifest.json **81aa7ea5f48a0c93762d629f43bbdeeb8672a2379a69e175641499b680838e3a** とfindings.json。元private snapshot/source/log/begin/manifestはwork/pgpt-runs/PG379各new-only run。

BUG1478は当21scopeCLOSED、BUG1479/YKT1240はguard不変更・六module最低一suite/実12件一致を確認し工具scopeCLOSED、完了2026-10-20。元v1=9686 actual1/0件not-run/NoTestsを維持し再解釈0。PTALT001/002代替0、実VM/DB/Unit/回収操作0、新全体/native/CHR/451正式/QA051final保留。正式1964/53・工数null・元/v3/v4未較正597.25は不変。次は残F03等の独立PG/PTへ継続する。
