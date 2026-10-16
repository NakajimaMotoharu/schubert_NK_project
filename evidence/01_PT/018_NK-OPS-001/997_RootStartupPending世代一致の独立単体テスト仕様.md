# 997 RootStartupPending.verifySelf 独立PT仕様

Program NK-OPS-001、class/method `batch.file.RootStartupPending.verifySelf`、RD OPS009/SYS002/004、UI251、SS343/SSC137（固定API/Web Root child launch同世代照合）。PG4662の残差のうち当methodの欠測条件を対象とする。Production/Main不変更、root/native scopeを取得しない純粋な相関検査であり、起動許可全体の受入とはしない。

fixtureは公開literalのboot46600001…/epoch46600002…、INV1234567890abcdef…、PID300/startTicks700、固定SHA a×64/b×64。期待値はSSのservice/boot/INV/PID/ticks全一致条件から独立に列挙し、Productionを呼んでexpectedを作らない。

| Test ID / JUnit method | 入力・操作 | 独立期待値 |
|---|---|---|
| PT-OPS-ROOTSELF-001 / exactBothServicesMatchOnlyTheRecordedChildGeneration | API/WEBを各一回、五識別値が全一致 | verifySelfは例外なし |
| PT-OPS-ROOTSELF-002 / eachIndependentForeignIdentityAndOtherServiceIsRejected | 各API/WEBに対し、反対service・bootだけ相違・INVだけ相違・PID+1・ticks+1を別入力。他全Serviceも固定識別値で入力 | 各不一致はIOException。PID一致だけ/他識別子一致だけで通過しない。MORNING等をAPI/Webへ読み替えない |
| PT-OPS-ROOTSELF-003 / absentBoundaryObjectsFailBeforeAnyNativeAuthority | launch=null、self=nullを別入力 | 明示null契約違反でfail-fast、native/DB/Unit操作は呼ばない |

関連suite `StartupLaunchRecordTest` は固定canonical frame/未知値/null/上限byte/不正IDを検査、`MorningStartupLaunchOwnerAdmissionTest` はowner側の期限/別service/未保持入力を拒否する。既成功を新件数へ加算せず、当snapshotで選択三suiteを実行した結果だけ記録する。

実行: clean固定後 `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes-runtime> python3 -B tools/quality/pg4666_root_identity_selected.py`。runnerはgit archiveの独立snapshotへMaven選択build、全compile/null解析、JaCoCo reportを実行し、事前にsourceから抽出した正確なclass/method一覧とXMLの全F/E/S0・重複なしを照合する。private反射/期待値Production算出/除外なし。未実行はnot-runとして残し、旧3721/nativeへ算術加算しない。

証跡はPG379/pg4666-root-self-identity-selected-v1のbegin/owner/manifest.safe.json、固定全入力SHA、Maven log SHA、XML SHA、RootStartupPending counter。実日時/対象commit/結果/coverageは実行後に別998へ追記する。class全体はawaitLaunch/observeの他native負分岐が残るため、当method成功だけでclass coverage100や全工程完了にしない。関連障害=追加PT段階で発見があれば修正前起票。現時点Production障害なし、初回TDD未実行。
