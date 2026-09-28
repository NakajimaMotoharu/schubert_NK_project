# 207 NK-OPS-001 Morning固定credential配布・単体テスト仕様書

Program ID: NK-OPS-001。対象: `schubert-nk-morning-controller.service.template`、`MorningServiceUnitTest.munit002NoUnscopedInputsOrSuccessOverride`。RD OPS-009、UI251、SS341§3/343§6.15、SSC-094、BUG-316/YKT-249。PG342。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MUNIT002 | Production Unit候補の全`LoadCredential`行を数え、`EnvironmentFile`/`PassEnvironment`/`SetCredential`/`ExecStartPre`/`ReadWritePaths`を確認 | SS343§6.15から`db-batch:/etc/schubert-nk/credentials/db-batch`が正確に1件。他のsecret、env fallback、任意pathは0件 |
| PT-OPS-MUNIT004 | Unit候補を`.service`名で隔離VM `/tmp`へ転送し、`systemd-analyze verify`。本番Unitは未変更 | syntax exit0。missing actual actors/材料の実起動成功へ読み替えない |
| PT-OPS-MUNIT005 | 別名のtest-only transient `systemd-run` 2件に既存固定sourceを`LoadCredential`し、秘密内容を読まずprivate file/dirのmode・UID/GID・link数だけstat | SS343§6.15のfile `0400:0:0:1`、dir `0500:0:0:>=2`、両exit0。test-only transientはProduction Morning UnitやDB接続の証明でない |

事前条件: host JDK25/Maven3.9.12、隔離Ubuntu VMのPostgreSQL/Javaと固定source metadata、既存PG323 test-only Morning Unit inactive/PID0。秘密byte、password、raw invocation ID、Credential内容は収集しない。REDはUnit修正前の同じPTを単独実行し、1件失敗を確認する。GREENはUnitだけ修正して単独3PT、Batch SpotBugs0、VM syntax/private copy metadataを確認する。Java Production source変更なしのためJaCoCo line/method/class/branchはこのUnit試験には非適用で、全体coverage100%やPG/PT合格へ加算しない。実行command、exit、branch/commit、入力hash、実際値、関連BUG/SSC、証跡hashは208とmanifestに固定する。
