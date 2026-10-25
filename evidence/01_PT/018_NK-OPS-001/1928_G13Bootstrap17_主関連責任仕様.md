# G13.07 Bootstrap/共有checkpoint17 source責任

2026-10-25 15:34 JST、G13_BOOTSTRAP17_SOURCE_V1/source64446不変更、開始.5/2/5pp・cap10。fresh06:33:04UTC使用1/残99/reset1793513544/secondarynull、現在窓残10以下/取得不能等まで自走、旧累計80/90停止なし。

source rootは`src/`。moduleとnamespaceを別に識別する。bootstrap moduleのapi namespaceをAPI moduleへ誤分類せず、batch module内共有checkpoint fixtureも完全pathで選択する。

|source|primary/cost|直接artifact/目的根拠|
|---|---|---|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/BackupCredentialLoaderTest.java|WBS-P018-01|InspectorCredentialLoader、BACKCRED001..008|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/BackupRequestCredentialLoaderTest.java|WBS-P018-01|同Loaderのrequest用固定入力、BREQUESTCRED001..008|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/BootstrapCredentialLoaderTest.java|WBS-P018-01|同Loaderのbootstrap専用名、BOOT007|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/EnumValueCatalogCompatibilityTest.java|WBS-P018-01|AesCredentialFileの識別値catalog、SystemManagerObservation03関連|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/InspectorDatabaseCredentialLoaderTest.java|WBS-P018-01|同Loader/DbCredential/AesCredential、INBOX197..201|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/MaintenanceOwnerCredentialReaderTest.java|WBS-P018-01|同Loaderのowner reader、MOWNER-READ001..003|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/PublicApiCredentialFixture.java|WBS-P018-01|ServiceCredentialReader/Setのtest-jar公開fixture、API-KEY006|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceNativeReleaseTest.java|WBS-P018-04|ServiceProcessResourcesの外側UNKNOWN保持、NATIVE-OUTER001。JVM未起動|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceOwnedReleaseTest.java|WBS-P018-04|同Resourcesのowned解放、SERVICEOWN001..004|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceResourceRetentionTest.java|WBS-P018-04|同Resourcesのrelease/outer-frame、NHOLD316001|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/ServiceDatabaseAdmissionTest.java|WBS-P019-01|ServiceDatabaseAdmissionの公開SQL fault fixture、DBADMIT001..004|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ChildBrokerTest.java|WBS-P018-03|ChildStartupContextのbroker literal、BROKERSTART001002|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ChildCaddyTest.java|WBS-P018-03|同ChildStartupContextのCaddy unit/cgroup、SSC178|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ChildMaintenanceInspectorTest.java|WBS-P018-03|同ChildStartupContextのinspector actor、CINSPECT001..004|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/NativeCoverageExportTest.java|WBS-P018-08|NativeCoveragePrivateFile/Profileのexport契約、NEXPORT617。native未実行|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/TerminalNativeCoverageProfileTest.java|WBS-P018-08|FixedNativeCoverageProfile/Checkpointのliteral roles/options、NC196001..004|
|schubert-nk-batch/src/test/java/dev/codex/schubert/nk/bootstrap/RootEntryCheckpointFixture.java|WBS-P018-08|FixedNativeCoverageCheckpoint/Profileのdata-provider fixtureのみ|

原Main担当/全関連/不確定を保持し、Loader/ServiceResources/ChildContext/Profileの原責任を変更しない。元9386v3/9246正常snapshot・現source hash/JDK SourceFile/CPを確認し、上literalの別parse・5選択/9catalog/8mapper反例/17近傍/旧885全canonical関連runtime/artifact witnessを照合。全17primaryの元Main集合membershipを事前に確認、明示module反例二つを試す。

public repo/保存classfileのbyte読取と工具metadata vectorのみ。target compile/load/init/JUnit/子JVM/native/実DB/credential/鍵/Root/VM/Unit/intent/permit/配備/遠隔操作なし。公開fixtureを秘密情報と混同しないがcredential実体は読み出さず、責任登録を権限/動作/実測coverage/PT成功へ変換しない。既成功確認再演/Currentbaseline/oracle変更0。

見込Java1710→1727/1789/Test745→762/824・残79→62、限定885→902、独立確認後だけ計上する。原941943/481484/見積受入意味・正式1964-53/17-190/工数null/QA051final/全current auditHOLD/全actualHOLD不変。G13.07一回の費用で共有fixture利用側へ二重加算しない。保存後も残62source/許可済み独立普通PGPTへ、小群/PMO待ちで停止しない。
