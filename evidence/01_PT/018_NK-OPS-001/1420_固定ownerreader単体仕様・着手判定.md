# 固定owner reader単体仕様・着手判定

NK-DAT-001/InspectorCredentialLoader.readMaintenanceOwner→readBackupMaterial、WBS-P018-01（485の所有先）、DAT009/OPS009/FIL006/UI212241251/SS343§6.4・SSC119/QA046。origin/main ce7e3c7b5の固定maintenance-owner copy/保持inodeとowner最大1024byteを独立根拠とする。loaderはopaque byte取得までであり、owner canonical parse/実Unit/期限/権限確認は後続契約のまま。

event1619、群見積.15/.45/1.2ppを着手前固定。PT_DEFAULT、自己TempDirと既Fixture/TestIoの明示synthetic metadata seamのみ、byteは公開ASCII'A'だけ。実credential/key/DB/Root/VM/Unit/network/permit/cohortを操作0、refusal不明範囲へ依存0。既Fixtureの乱数鍵も自己生成・終了時消去・証跡非出力、実鍵ではない。ファイルは自分で作成した一時fileだけ、運用owner/currentへアクセスしない。

|TestID/method|fixture・操作・独立期待|
|---|---|
|PT-MOWNER-READ001/owner001LiteralBoundsAreCallerOwnedAndScratchIsCleared|1/1024 ASCII'A'を固定maintenance-ownerへ書く。maxRead17で分割read。全byte一致、返却copy消去後も原fixture file不変、open/close各1、全scratch1025byte消去|
|PT-MOWNER-READ002/owner002MissingFixedNameEmptyAndOverflowDoNotReturnBytes|別名だけ存在→fixed filename missingでopen0。size0/1025/65537を各fresh fixtureで拒否。固定InspectorCredentialException/message/causeなし/suppressed空、全開放とscratch消去。SS上限1024＋検出1byteを根拠としProduction戻り値からexpected生成しない|
|PT-MOWNER-READ003/owner003EveryIoAndCloseFailureWithholdsTheResultAndClearsScratch|root/file属性、open、read/short/zero/lying count、size-after、close、root-final等の既fault port。全例外は固定診断、open=close/scratch消去、返却なし。close失敗を正常結果へ変換しない|

戻り値が有効なmaintenance-ownerであるとは主張しない。ASCII'A'はreader境界用だけ、owner parserの正常goldenを捏造しない。正常/上下限/欠落/例外/後条件が対象、nullは引数無しの本wrapperでは非該当（loader constructorとIo非null契約は既試験）、並行/再送は本群で新しい契約を導入せず既file loaderの別scopeへ残す。

PG点検：固定名/1024制約、channel/entry close前の返却なし、buffer finally消去、metadata前後照合・同device・固定redactionを確認。新Main修正は試験で不一致があれば915先行、なければ不要な変更0。新Test-only一class、既oracle/Main/gates不変更。選択6520は基準12＋新3=15/8、format→全六testCompile→PT/static、6522は原XML/851Main/1667/六Jar/PMD-CSを照合する。動的PTを隠した静的代替ではない。

反復driverの転記を減らすため同じpinned engineの三phase/六module/immutable snapshotを有限profile helperへ集約し、元6512/6516工具は不変更。helperの管理positive/negative/命令列順を別checkし、Production PTへ加点0。新only slot/真正終端・failed/skipped/flaky拒否を維持する。実行source/command/exit/hashは結果へ。旧全4064/新20/15へ算術加点/coverage合成0。

事前定義確認：formatter35958終了0、`python3 -B -m unittest finite_selected_profile_test` 四件/F0E0。全六inventory・format/testCompile/PT順序・失敗phase/partial coverageの昇格禁止・Main/gate違い拒否・reader元source/空Main差分を検査。TestSHA `dd7d997f90c5c15f7cc61a8f89094f7ce459f8609d87c528cee68a63e5164053`。pinned PYTHONPATHで6520一回、真正0後6522のみ。usage9687b032（22:15:26）N/Tnull/既cursor継承。
