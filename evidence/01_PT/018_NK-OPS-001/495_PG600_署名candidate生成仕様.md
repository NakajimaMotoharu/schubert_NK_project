# PG600 署名candidate生成仕様

WBS-P018-02既共有枠0.5/1.5/3.5週次ppを着手前固定（PG599全回帰K01別、重複費0）。分類5：PG-D397、SS343既code-only/187artifact/schema028の候補生成契約内、起動権限・SS/RD/UI/oracle変更なし。候補を作るだけでcurrent/approval/permit/DB/Unit/親を変更しない。

対象 `pg600_candidate_contract.py` / `pg600_candidate_build.py`。Test PT-OPS-PG600-C001：独立literal六module・許容三変更三interface追加をcount12で受入、module欠落/追加・class除去/未知追加/追加欠落/他変更/必須変更無し/空/不正digest/不正名/NULLを拒否。C002：認証済旧BOMa224の全187実payload/hash/size・symlink無し/全inventoryと新PG5993457/511/六静的0/全XMLhash/frozenjarを合同し、全1603byteの限定deltaを検査。旧rowを新rowとaliasにせず独立に保持する。

入力：旧私有 `PG379/pg548-release-v1` とfresh `PG379/pg599-candidate-bootstrap-six-host-v1`（source23b14a44b10504172e030bbd6625926bf049fb5c）。期待：新only `PG379/pg600-release-v1`、VERSION=0.1.0-PG600、schema028/SQL28/history29/187artifact不変、許容projectjar及びVERSION以外byte不変、bootstrap jar三配布先同byte、BOMsource23b、Ed25519既pinでsignature64byte検証成功。秘密key/私有署名log/credentialを公開せず、safe hashだけ記録。

実行：`python3 -B tools/quality/vm/050_s1/pg600_candidate_contract_test.py`、Pyflakes、source固定commit/push後 `python3 -B tools/quality/vm/050_s1/pg600_candidate_build.py` 一回。生成失敗・既出力・署名未知は再使用せず保持、失敗修正前BUG/YKT。工具fixtureはProduction PTへ加算0、sourceの全coverage/native/正式はPG599と後続実VMで別照合。

23:01時点：作業領域の独立二tool test/変異条件はexit0、Pyflakes0、未署名/未生成/未配備。受入はactual出力/hash後に更新する。
