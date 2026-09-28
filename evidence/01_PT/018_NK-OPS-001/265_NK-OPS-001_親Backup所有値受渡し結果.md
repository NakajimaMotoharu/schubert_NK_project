# NK-OPS-001 親Backup所有値受渡しPT結果（PG377、限定）

仕様[264](264_NK-OPS-001_親Backup所有値受渡し仕様書.md)。2026-09-29 JST、`dev-foundation`、source/test/spec固定commit `d9a20b97e21227124384e8db32d40083bbca4e35`。Linux 7.0.0-34-generic x86_64、JDK 25.0.4、Maven 3.9.12、Node 24.19.0、SpotBugs 4.10.4.0、JaCoCo 0.8.15。local Maven repositoryは`/home/mini/codex/project1/work/toolchain/m2/repository`。

`PT-OPS-MBSTAGE005～008`を含む`MorningBackupStageTest` 8件はF/E/S=0。`executeOwned`が同一callbackに借用させるstate・DB access・公開済request・両begin・partの識別性、fresh/recover、失敗時close、null拒否を固定fixtureとイベント列で確認。期待値はProduction返値から生成しない。選択試験・Batch SpotBugs・JaCoCoはexit0で、追加method `executeOwned`のmissed instruction/line/methodは0。ただし`MorningBackupStage`全体の旧native fresh/resume等はmissed instruction49/line16/method2、匿名classはline2/method2/class1が未網羅。branchだけを見て100%とはしない。

security/所有境界変更のためProduction6を同sourceで`clean test`しexit0。369 suite、2,513件、failure/error/skipped各0。初回全6 runはNode.jsがPATHに無くWebのbrowser script 2件でerror、Batch未実行のままexit1だったため合格算入しない。2回目は既設Node 24.19.0を明示して全6を再実行した。SpotBugs6module指摘0、JaCoCo report exit0。最終runのmissed instruction/branch/line/method/classはProtocol `0/0/0/0/0`、Storage `0/0/0/0/0`、Bootstrap `60/37/11/4/0`、API `95/3/32/4/0`、Web `80/1/25/4/0`、Batch `1539/31/350/129/15`。全4指標100% gate未達。NullAway等の別正式gate、全scope collector、秘密scan、実OS親M/A・Unit/permit/外部Web/API・CHRはこのrunで実施・認定していない。

実行commandは`PATH=<Node24 bin>:<system paths> JAVA_HOME=<JDK25> ./mvnw -B -ntp -Dmaven.repo.local=<fixed local repository> -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch -am clean test`、続けて同6moduleへ`spotbugs:check jacoco:report`。source/test/config/toolsは2回目開始から結果収集まで不変更。Test XMLとJaCoCo XMLのSHA-256および集計は[manifest](evidence/provisional/PG377-owned-backup-stage/manifest.json)。raw XML、credential、tokenはGitへ保存しない。

関連：RD OPS-009/BAK-001、UI251、SS341/343、SSC-092/094/104/105/107/108、BUG-322、YKT-254、471 R1/D04/05。実parentと子Backup Unit・同原本再読・archive/issuer、R2/R3と実NK CHRは未受入。正式認定`PT-WEB-20260925-24`/source `858713c0bf310ae8bf62078b0a1cedbce4e968db`、中心進捗48.3%は据置。
