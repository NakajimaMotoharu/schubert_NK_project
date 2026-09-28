# 474 R2停滞の限定review・検証仮説

2026-09-28 JST。471 §5の約20pp点検。これはPG/PT受入・新規正式試験認定・上位仕様変更ではない。実装を停止してPMO返答を待つ資料でもない。

## 観測事実

- 共有週次使用率はcheckpoint158の31%からcheckpoint176の50%へ約19pp増えた。R1のroot/backup/Cleanup下位条件は増えたが、R2 Production外部起動・R3実NK CHRは0、D01～D07のclosed/reopened/newも0/0/0。共有枠の増分をこの作業だけの消費量とは断定しない。
- 最新source `a1898417f`の6module限定全回帰2,327PT/342suite F/E/S0・SpotBugs0。ただし `clean verify`はBootstrap coverage100% gateで停止し、Batch native新classもcoverage不足。正式run/sourceは2026-09-25の`PT-WEB-20260925-24`/`858713c0bf310ae8bf62078b0a1cedbce4e968db`のまま。
- 隔離VMで固定8のCaddy/Backup/Artemisはloaded inactive/PID0、Web/API/Cleanup/Inspector/Expiryは正規Unit not-found。PostgreSQLはactive。Morning controllerはBUG-314で誤照会を訂正：正規`schubert-nk-morning-controller.service`はloaded inactive/PID0、PG323 test-only probeをExecStartに持つ既存oneshotでありProduction資格なし。Cleanup/PG339候補Unitは`/tmp`で構文確認しただけで、設計どおりinstall/startしていない。既存Unitを上書きしない。

## 最小再現と原因仮説

真正VMの固定Unit `systemctl show`だけで5対象not-foundを再現できる。PG335のRoot/whole-Unit観測はnot-foundを成功へ補完しない。SS341/342/343では親Morningの連続M/A、固定8実Unitの停止・kernel終端、current失効、同run backup/cleanup、permit発行がArtemis→API/Webの前提であり、子Cleanup read-only preflightだけではその入口を作れない。約19ppの実装は子の安全条件を詰めたが、親・配備・起動の直列ボトルネックを閉じていない、という仮説を次区間で検証する。

## 次区間の変更

1. PG335証跡を固定pushした後、親Morningの真正入口と連続M/Aの所有・固定8 policy/stop/terminal・unknown隔離を一つの受入経路として組み立てる。新部品の選択PTと実VMの初回安全拒否を保存する。条件不足をfalse成功やfake Unitで埋めない。
2. 8実Unitのうち未配置5対象は、対応するProduction entrypoint・credential・実効systemd policyが成立してから非起動配備/観測する。特にCleanupはread-onlyの現候補を0/10 Unitへinstallせず、同run backup/DELETE/transferの成功・失敗契約を先に完結させる。
3. 受入判定は「真の親を通じた実PID/readiness→同経路のCHR-A01/L01」に固定し、選択PT増分やUnit構文成功をD closed/R2に加算しない。次の10pp点検でも親経路の実接続が進まなければ、依存/検証単位を再度修正する。

依存SSは341 §2～5/8・342・343、品質は451、最新実績は456、具体残件は460。SSC104は設計範囲内の親子接続として継続し、上位RD/UI変更は現時点で不要。新たな設計矛盾を発見した場合は914を先行し、承認が必要なら分類どおりQA等を先行する。
