# 1307 有限保持PT v1：fixture stream寿命エラー（不合格）

元exec22229/pg6164-native-retention-selected-v1、source **f2273aac71569e671b3ba1805f19479cd9dab864**、2026-10-20T19:36:06.587417Z～19:36:57.691778Z、真正1/Maven1/phase[0,1]、入力固定。予定25/13に対し実7/4（F0/E1/S0）、残18/9 not-run。protocol/storage静的0のみ、BootstrapがTest errorで止まったため後段静的/target coverageは未測定で、placeholder0/0を100へ補完0。

不合格=ServiceResourceRetentionTest.hold316002、IOException Stream closed / OwnedRetentionProcess.assertHeld line41。最初のchildで固定UNKNOWN診断/CLOSE/実interval・143までは確認したが、Process.destroyが検査pipeを先に閉じ、EOF検査が例外となった。保持/回収の途中事実を当PT合格/native/Root資格へ加算0。新childは143終了済み、fallback回収も同Process handleだけ、旧VM/既job操作0。

私有PG379/pg6164-native-retention-selected-v1/：begin.safe.json **ed80f6ff673d23b95d41aa0c915ad833541f1cd0c620d385bed3cc923b32391a**、source.tar **1bd1f3ba3bf381ab6a5c2a5a04c7b2a78795cea53ee849a4458452dd203f0905**、manifest.safe.json **9f137fc89ff23a5e01fa82e59d686798d8b853a8dbd7f9f0b32e2843bc7c7be1**。元command/environment/exit/XML/private logを保全、raw秘密公開0。JDK25.0.4/Maven3.9.12/Node24.19.0、PTPRE040/1306。

BUG1558/YKT1315を修正前起票、body signalを生成Process由来の世代付きProcessHandle.destroyへ限定訂正。検査reader/元期待/Production/品質条件は不変更、回収後EOF/外側markerなしの検査を削除しない。new-only6166-v2で同25/13を実行し、原v1を再発行/上書き0。S3b後半・当source全体/native/CHR/451/trace、正式/工数null/QA051final/PTALT対象不明・実環境安全HOLDは別未完。
