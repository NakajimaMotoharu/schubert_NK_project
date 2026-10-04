# NK-OPS-001：PG458実行結果（継続中）

326仕様に対応。正式認定・IT/ST合格ではない。Production source=`ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a`、code-only工具は後続dirty成果として別hashを保持。安全manifestは018/`evidence/provisional/PG458-caddy-timeout-full/manifest.json` SHA9357f776614877674b9ac64e7791bdd385b8befbe35598ff04233e0ce77db8fdと`PG458-code-only-v1/manifest.json` SHAdceb38b290b6e008ec47c0166465853f4f9c83a68980ad611fcae9af7f885abc。

| Test ID/実行 | actual/証跡 | 認定範囲 |
|---|---|---|
| FULL458001/full-v1/session53552 | **0/3254PT480suite/FES0/SpotBugs6module0/NullAway compile成功**、00:04:17～00:21:40JST、rawSHA002f53ca… | 全6targetをprivate pg458-hostに完全byte一致保存、前後sourcehash一致。Parent/Nativeのmiss有、100/正式未達。旧Source3249や中断2494を加算0 |
| runtime/assemble-v1 | 1/regular input required | BUG678、Maven default dependency対fixed runtime-dependencies契約不足。partialfixture/source/失敗保全、署名/VM操作0 |
| standalone metadata-v2/session6910＋独立guard | CLI0/guard1 | BUG679、同GAVのm2旧shared byteを独立比較で拒否。全newruntimeをprivate pg458-stale-runtime-v2へ保全、新候補生成前で停止 |
| runtime rebound/独立proof-v3/assemble-v2 | **0**、元full全6集合/GAV/count1,1,9,38,55,41・6主jar・全内部shared jar完全一致、proofSHA6f85fc31… | 同回帰実byteだけからnew-only候補生成。plain metadata以外の再build/再jar/再PT0。未来runnerは固定runtime/plainを明示、当full実commandは歴史のまま |
| CODE458001 | Werror0/独立42assert0/ProductionPT0 | 引数・namespace/foreign/null/intentの工具vectorのみ。native/Production coverageへ加算0 |
| CODE458002/stage33553/verify47781 | **各0** | pinned署名/fullBOM27/既存currentPG456/source559から全9kernel停止・261全14列/23business/旧原本pending/Backup20/Transfer/configAssetを真正M/A/DB/readonlyschemaで再照合。新permit/start/DDL0 |
| CODE458003/activate58920 | **0**、全owned callback正常帰還 | current/approvalPG458・fresh currentbootINVALID、signed Unit delta0、既存27SQL/profile/Caddy設定・全DB/原本/Backup保全。rawとprivate SAVEはroot0700/0600、old/run復元・旧復旧/DDL再発行0 |
| native観測v2/stage31579 | 0、新only2Python byte/source/Root0500files0400 | 旧watch保全、非安定manager/kernelは親bind/assert前も再観測。20独立samplingassert0は別工具結果、全体受入0 |
| PARENT458001/外部start | command0/PID162624/Invocationfb3eaf763a8c4a5e8172d3c42f8fc954/job68651、**実行中** | private O_EXCL発行guard/receiptから一度のみ。hostreadonlywatch session16833に再付着、親30分budget不変更。start受付はPT合格/親完了ではない |
| CADDY458001/DONE458001/実CHR/native正式 | 未実行又は受入待ち | 同Source親API保持Web/全ready/CaddyTLS/原本DONE/live intent退役/全outer正常0or10と同byte coverageを完了まで継続 |

旧Source559のtimeout143/旧BUG544/YKT388/旧工具終了不明・Currentbaseline・原本Backup・stash7を保全。旧PT execもnative新実行前にprivate archiveへ保存（SHA2b609af9d2657f19b92661ea802e193cb9c66e83d88a172736319d314aeee579）。coverage append=falseの新execを旧結果へ混ぜない。新stage/verify/activateの開始終了時刻は元commandで保存されていないため、manifestに不足を明記しcollection時刻で捏造しない。

現在値/process/log/利用枠/次commandは456先頭に集約する。通常試験成功・配備・報告で停止せず、稼働親へ再付着し同接続経路を受入まで閉じる。
