# NK-OPS-001 / NK-WEB-002 Web部分所有・request整合PT仕様

## PG-D377同群追加（PG472）

HEALTH001..004/WebRuntimeHealthTest：10条件を一つずつ否定したliteral falseと短絡順、全正常のexact call順、3provider各例外identityと後段未呼出、owner通知例外identityを独立に確認。actual captured資源のpresence先行条件・本番method referencesは従来どおりで、providerや所有の差替えはない。

STOP001..005/WebRuntimeStopTest：literal30秒/28秒/25秒、全phase順/再close0、失敗phase以後保全/同phase再試行/元期限不変更、exact期限でremaining0/期限超過で固定失敗・次phase0、IOException/LifecycleException/runtime固定redacted例外、direct/nested Error元identityを確認。独立AtomicLongで境界を制御し実native期限を延長しない。

PT-WEB-IDENT-CONSIST002/003：verified contextのUUIDから未設定requestIDへ一回保存（generator0）、正規Caddy loopback/単一XFF/Proto=https後context保存だけをargument/state例外で拒否→固定例外/cause0/suppressed0/chain0/既ID保持/context0。BUG759はこのfixtureのProto欠落で先行403となった失敗を別保持し、Productionを変更しない。

PT-OPS-NWEB-UNKNOWN001/WebUnknownRetentionTest：既JaCoCo agentだけを引き継いだ隔離子JVMで実retainUnknownをdaemonへ実行し、同methodのTIMED_WAITING/closed0→interrupt flag消費→同frame/closed0を観測。子fixtureのみ全終了してdaemonを終端し、実native borrower/UNKNOWN成功markerは生成0。15秒上限/親finally実child後条件/秘密0を確認する。

WebProcessMainTest OPS-WEB-MAIN001にStartup引数版のargv拒否（status70/IO0/startup0）を追加。PG472-v6は同五module・13suite・69PTの群とし、正式受入はsource固定fresh六moduleと同source実nativeで別実施する。v4/v5 failedは合格へ算入0。

関連RD SYS002004/AUT002004/MON003、UI212/222/226/252/253、SS313314321342343352/SSC172、451。PG471の実native8streamから得た不足を根拠に、既仕様の否定側を独立fixtureで追加する。production sourceは変更せず、未起動を実稼働成功・native100の代用にしない。旧full3328/native8/formalrun24は別sourceの正式合格へ流用しない。

| Test ID / class.method | 目的・fixture・操作 | 独立期待値・根拠 |
| --- | --- | --- |
| PT-OPS-NWEB-PART001 / WebNativeRuntimePartialTest.part001 | synthetic固定5credential、全DB呼出でfailするDataSource、promotion count付きReady、既定config。未start healthy/ready、ownerStopping通知、close2回、stop後start | healthy/ready常時false、promotion0、DB0、close通常return、再start IOException固定`Web startup unavailable`、borrowed AES版vはclose後も利用可。SSの部分owner・取得資源だけclose・停止後再start禁止から手書き期待値 |
| PT-OPS-NWEB-PART002 / part002 | Ready.informationで独立IOExceptionを投げ、releaseはfail | 同じprimary IOException identity、DB/昇格0、borrowed credential不変更。production methodでexpected生成0 |
| PT-OPS-NWEB-PART003 / part003 | database/credentials/config/Ready/stop supplierを個別null | 既存construct前fail-fast契約で拒否、資源取得/昇格0、nullをcatchして正常化0。保持後の予期しないdereferenceは許容しない |
| PT-WEB-IDENT-CONSIST001 / WebRequestIdentityConsistencyTest | 明示literal UUID2個/検証済みcontext1、内部requestIdを別UUIDへ替える→元IDに戻す | mismatchは固定IllegalState/置換ID生成0、context identity/既attributeは不変更、一致時は元UUIDを返す。SS313/SSC172の一request一identity、不信HTTPheaderへのfallback0 |

環境：hostJDK25.0.4/Maven3.9.12、branch dev-foundation。実行=`bash tools/quality/vm/050_s1/pg472_web_partial_selected_v1.sh`、既関連main/lifetime/credential/protocol/storage PTと5module static/format/NullAwayを一群で実施。fixtureの既安全LoaderTest補助を再利用し、実password/key/DB/master/sessionは使用・Git格納しない。sample secret copyはouterfixture終了時にzero-clear検証、raw値をlogへ出さない。

目的はPG471不足WebNativeRuntimeのnull resource/停止済み/start拒否・request consistencyを減らすことであり、broker/replay/HTTPの故障・30min/nativeScope全網羅を本4PTだけで宣言しない。実source/command/時刻/actual/XML/coverage・全hash/関連障害は355及びsafe manifestに追跡。未実行・中断・failed/skipped/flakyは不合格、coverage増分は実counterから算定し無意味なassert/除外0。新production/横断変更が必要なら別群として先に設計・台帳と独立oracleを確定する。
