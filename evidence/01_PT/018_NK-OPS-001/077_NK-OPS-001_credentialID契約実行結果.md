# NK-OPS-001 credential ID契約実行結果

PG280/SSC-081、PT-OPS-CREDID-001～004。2026-09-25、branch`dev-foundation`、JDK25.0.4/Maven wrapper/Linux。Storage module `spotless:apply verify`はexit0、全Storage coverage gate PASS。正式全reactor/53scope/hash/source commit固定前のため本段階を正式合格へ算入しない。実credential内容/ACL/OS配布は未試験。

正式限定認定: source`bc47a87e4c11462ce5409c314b8e1b383e0fa6d5`、`PT-WEB-20260925-18`（06:40:22～06:52:54 JST）、command `sh tools/quality/030_run_pgpt_verify.sh PT-WEB-20260925-18`、exit0。全1,943PT（CHR41/Protocol80/Storage101/API767/Web550/Batch404）、failure/error/skipped0、Production Java6 module instruction/branch/line/method/class missed0、SpotBugs0、103負canary/53scope/hash保存照合PASS。CREDID4件4/4、root manifest SHA-256 `c8e625ae0c9ed4ec1d51c6f4cdf98b7b5d45192d39751abcc9d88506bd87fbd0`。独立期待値は076、Test ID→method/実際/環境/coverage/source/証跡hashは同Program sanitized manifest/results。実file読取・ACL/OS配布・credential codecは未試験でSSC-081継続。新規障害なし。
