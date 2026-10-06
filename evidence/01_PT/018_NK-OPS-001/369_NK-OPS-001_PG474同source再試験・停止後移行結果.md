# PG474同source再試験・停止後移行結果

仕様368/366、PG-D379/BUG762/YKT542、SS312321333342343/SSC193194195/451。Production source09b448644cfe70c87df9c89aa5c0c1bf6efdeeea、tool HEADは後続保存commit、branch dev-foundation。OS host Linux/guest Ubuntu26.04、JDK25.0.4/Maven3.9.12/JaCoCo0.8.15。私有証跡はWorkPG379/RootSAVE、raw値・credential・native/heapはGit非格納。

|Test ID|実行・独立期待／実際結果|
|---|---|
|PT-OPS-API-FRESH474001|pg474_full_v2.sh source09b、10:40頃～10:57:51 JST/session1517 actual0、3365PT505suite/FES0/static6zero/NullAwayWerror、strict pg474_collect_full_v1.py v2/session30092 actual0。六byte/source/前後SHA一致、五class全LINE/METHOD/CLASS/BRANCHmiss0。旧full-v1の品質拒否を合算0。safe PG474-api-consumers-full-v2/manifest SHA1ccb9270840213ca8147b72d86c3d1a24822756e42820947df58d5470a6822b4。BUG762/YKT542対象完了、全global100とは異なる。|
|PT-OPS-CODE474001|pg474_candidate_build_v1.py/session13408 actual0、186artifact187canonical/27SQL/11projectjar同frozen-v2、署名64B/既pin独立検証。pg474_stage_candidate_v1.py/session72664 actual0、old current不変更・start/DDL0。digest3f6b837c12282baca8b2c5fc79c85916421b6940471cca5d544381072120af18。|
|PT-OPS-CODE474002|pg474_stopped_compile_v1.sh/Java71独立assertion/Werror0、helper153/inventory37/control265/term240 actual0（工具assertionはProduction PT0）。stopped stage→verify/session61719 actual0、11:07:32～34 JST。真正全9停止/旧normalDONE/391全14/postL01全23business/57metadata/原本Backupを実照合し未使用候補のみRO化。|
|PT-OPS-CODE474003|17exec＋2heap全19の実byte/SHA/元metadataとRoot0600コピーを区別して全保存。legacy empty1は元mode640/emptyを維持して成功補完0、heapはcoverageへ算入0。RootSAVE pg474-stopped-deploy/native-before.private.json SHA780303726e974bc0cac808abbce62b5d02744d77c7e02554158290c9375d1a5c。|
|PT-OPS-CODE474004|pg474_stopped_activate_v1.sh/session6258、11:11:39～43 JST actual0、全new M/A/DB等scope通常帰還、current新PG474/同activation INVALID、old UNKNOWN正常化0・DDL/start/stop/permit0。complete.private SHAc7cf0c4285cb0ebe3ddaa26fa74cf3a47669fc65de3ed60a0363216ba5a30315。|

安全manifest evidence/provisional/PG474-stopped-code-only-v1/manifest.json は生成初稿のTest ID/Java source hashが旧Pg473を指した記載を訂正した（Root/private実行証拠・実結果は変更0）。訂正後hashはGit保存時sha256sumで照合。spec368四ID・当結果・工具の対応を統一。工具の本体/期待値の変更による再実行ではない。

後続実親は11:12:50.857950 JST一回、2885306/INV299a11cf4c814775b3c37970decc602b/job214231、元30分期限維持。observer94740へ再付着し、Root普通/保持APIWeb/Caddy/A01/真正DONE/readback/ownedTERM/新8nativeは別受入で継続する。通常切替完了で停止0。正式run24/1964PT53scope48.3%・globalcoverage100/QA051比較/BUG544原因/ITSTは未認定。
