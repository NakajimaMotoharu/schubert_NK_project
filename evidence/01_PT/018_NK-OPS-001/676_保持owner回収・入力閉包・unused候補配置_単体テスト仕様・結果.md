# 保持owner回収・入力閉包・unused候補配置

Program NK-OPS-001、関連RD SYS002004/OPS009/MQ008010、UI212243251253、SS311312342343353354355、SSC274275/QA047、BUG1150～1153/YKT918～921。Production候補2741c4546afad6c1e8b6efbd53dfb58144edf7bb/test1683dd9f6de00e71d2317d9af3cd50400a37bf4e、VMcurrent4d6/PG1544/boot3d69。正式1964PT/53scope・wholeleaf受入増分0、IT/ST未実施。

| Test ID | 対象・独立oracle・結果 |
|---|---|
| PT-OPS-S274-PAIR-001 | 1664：実PID/ticks/argv/全task親子/101-4FD、M属性3FD・Adup同OFDとsoleFLOCK、DB role/app/backendStart・双方向socket/soleadvisory・子唯一bus、全24-32-187/元原値/native14を二読。候補未配置・signals0、actual0/proof c0036f9a79672f32ad9c51453b7ca16e067d4ec34cc183d6321ab63b42fe0e8a。 |
| PT-OPS-S274-TERM-001 | 1667：同接続freshproof b842…signals0耐久完了、Ref一回普通TERM/有限reap/bus消失成功。親予約後guard拒否、actual1/send前例外を固定payload/AST/stackで独立照合、親TERM未発行。別SSHが共有/run二時刻を更新したBUG1152、旧結果を合格へ加算0。 |
| PT-OPS-S275-SOLE-001 | 1672：当子pipe100/101だけ消失、99FD親/子0/同DBpeer-MA/全原値を独立再認証、actual0/proof537aaccf3ff3f98e17e71dbda28fa7bfe671e44699f9b7d59c6fde9241dd93aa。 |
| PT-OPS-S275-TERM-001 | 1674：host排他gate/同接続fresh8a5b856…signals0耐久保存→当親一回普通TERM/15秒pidfd終端通過後、proc有限reapでESRCH例外actual1。元place host16309はterminal143/log647fa41d…、closeUNKNOWNを保持。旧予約・TERM再送0、BUG1153を先行起票。 |
| PT-OPS-S275-POST-001 | 1675：固定旧payload/stackのTERM後ESRCHを独立照合し、旧actual1/complete無しを維持。別fullpost actual0、親子/DB/advisory/MA0・新十Ref正常、全24-32-187・原本Backup/runtime/native不変、afterSHA9f18…を実証。全体・旧scope正常closeではなく今回の資源後条件のみ閉鎖。 |
| PT-OPS-INPUT-001 | 新1681 pure contract：独立literal input3basename、missing/extra/suffix/foreign-import/transitive-helper欠落/pathescape/class欠落/hash/null/bool/相対importを拒否。STD固定順序、全Python actual生成static0、Java実preflight呼出はM/A取得前。input/source期待値をProduction methodから作らない。 |
| PT-OPS-INPUT-002 | 新1682：Werror実0、argument6/label16/original18/currentidentity13/inputboundary5の5独立Java群実0、141相対file/hash凍結。source1f886a0e6404e307e52a0464a20e8b5ea28ceace、archive3ebc5be9…/署名5e32…/bundleを保持、guest mutation0。 |
| PT-OPS-INPUT-003 | 1683 stage actual0（13:13:03～13:13:07UTC）、実141byte/hash・新only root所有400/700を検証。place actual0（13:14:08.813799～13:14:52.870369UTC）、実入力閉包preflight→current署名/全BOM/4identity→真正元DONE→unused候補187配置→正常DB/Ref/M/A返却。current/approval/epoch/Unit/SQL書込/reload/start-stop0、旧失敗slot未変更。 |
| PT-OPS-INPUT-POST-001 | 1685別fullpost actual0、unused候補187/manifest/SHA256SUMS/署名・owner/mode/link/ACLを独立確認、schema028/history29/Source2741/BOM195e…同値。before/after全SHA9f18…/全24-32-187current/原本Backup/runtime/native14・旧owner-peer-advisory-flock0/新Ref正常。候補はまだhostRO/currentではない。 |

環境：host固定JDK25.0.4、Maven3.9.12（今回Production Maven再実行なし）、pyflakes3.4.0、隔離LAN VM Ubuntu26.04.1、固定boot3d69。実commandは固定PYTHONPATHで `pg1664_current_unused_pair_readonly_proof.py`、`pg1667_unused_pair_once_handoff.py`、`pg1672_remaining_db_owner_readonly_proof.py`、`pg1674_remaining_owner_once_handoff.py`、`pg1675_remaining_owner_independent_post.py`、`pg1682_closed_candidate_compile.py`、`pg1683_closed_unused_dispatch.py stage/place`、`pg1685_unused_candidate_independent_post.py`。各予約slot一回、失敗slot再実行は禁止。

工具選択試験：同1f886相当sourceで8suite21成功（1664/1665/1667/1672/1674/1675/1680/1681）、新1685独立1成功、全新生成static0。BUG1151の正規SendSIGKILL設定名誤検出はAST操作判定で是正、旧1failureは維持。ENOENT/ESRCH＋現在absentだけ合法、他errno/PIDreuse/存在再開は拒否。これらの工具試験を3596Production PT/coverageへ算入しない。Production全6同source3596/532/1643/static6zeroは675へ参照、新source host残L3772/M626/C37/B1085・native NOT_RUN/global100falseのまま。

公開hash対応は `evidence/output/676_manifest.json`。私有raw（DB/原本/Backup/FD/traceback/秘密・credentialを含み得る入力）はGitへ格納しない。SSC274 source70873001b→main532da318b/PR116、SSC275 sourcead9b46bde→main868930595/PR117は設計only regularmerge、app添付100identity上限errorは保持・既添付削除0。次=同候補hostRO/full verifier→普通新current公開→当Source真正親/正常ownedstop/native→CHR/四100/正式451/trace/引継ぎ。
