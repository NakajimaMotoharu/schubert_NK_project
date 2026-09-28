# NK-OPS-001 RootServiceLauncher 実外部拒否限定PT仕様（PG375）

Production `RootServiceLauncher.main/run` の隔離VM root外部JVMでの**非成功**契約だけを確認する。RD SYS-002/004/OPS-009、UI212/251/253、SS311/342§4.2/343、SSC086～089、R1/D04/D05、PT-OPS-RMAIN001～006。Production Web/API Unit・原本・currentは変更せず、root Launcherの同PID exec/業務起動はまだ認定しない。

| Test ID | 事前条件・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-RMAIN007 | PG372同source classを別classpathで固定、隔離VM実root JVMへ`WEB`単一argv | 必須gate欠落時はexit30。stdout/stderrにcredential/診断値を出さず、Unit/permit/current/DB/markerを変更しない |
| PT-OPS-RMAIN008 | 同じく`API` | exit30・秘密非表示・上記不変更 |
| PT-OPS-RMAIN009 | 既知外`OTHER` | argv契約違反でexit70、read-only前段も開始せず秘密非表示 |

終了前後のProduction Unit/固定namespace・実行PID終了を確認する。Production classの返値を期待値作成に使わず、30/70はSS342/起動失敗閉鎖契約のliteralで固定する。生環境・資格情報・raw session/tokenをGitへ保存せず、command/exit/OS/JDK/tool/hash/前後状態・coverage未認定・関連BUG/SSCを261とmanifestへ記録する。root VM negativeはgate順序/真正許可、同PID置換、Web/API業務ready、CHR/R2合格を証明しない。
