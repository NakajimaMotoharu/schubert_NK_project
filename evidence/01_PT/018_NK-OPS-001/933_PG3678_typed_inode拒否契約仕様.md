# typed inode fixtureと値境界の独立試験

Program NK-OPS-001、RootServiceExecutableAdmission.checkedAttributes・RootServiceExecutableAdmissionTest、SS343/SSC137/143、BUG1312/YKT1078、PT-ROOTELF-3678-001～003。Java25/PT host隔離、実VM・Root・ADMIN操作なし、Main/source4856は保持。

001：現行Testの混在wrapper三項式をJava25で実評価し、Integerを意図したuid/gid/modeがLongとなる修正前再現を保存する。既成功PTの再実行ではなくfixture不具合の独立反例。002：明示Object分岐にして全fixture実classがliteral期待Integer/Longに一致することを先にassertし、値不正をIOExceptionとして拒否。003：root uid/gid=0、directory040755/nlink>=2、file0100755/symlink0120777/nlink1、dev/ino非0、size>=0/file1～8388608、FileTime二項、非symlink ACL空の独立Unix literal仕様を許可/境界/型/欠落/null/ACL例外で確認。値やexpectedをProduction methodから生成しない。

型・値不正はACL取得前拒否、symlinkはACL呼出し0、正当file/directoryは一回/引数44を別counterで確認。元型不正反例も残す。関連固定snapshot Mavenで実Test ID/XML/FES0/format/lint/NullAway/SpotBugsと当method branchを評価する。coverage未達は未達で記録し、人工reflection/除外なし。残5匿名classは実Root/nativeが必要な旧entryであり、coverage目的だけの新業務起動は行わない。まず意味あるhost boundary群を進め、必要な同Main全回帰とnative再資格は群をまとめて実施する。

費用は487 group開始値を参照、今回群subset低0.3/標準1/高3共有pp。485でRootServiceExecutableAdmissionの主担当は**P018-03**であり、初期group event0937のN15.02表記はnative採取責務との混同だった。後続eventで担当だけを訂正し、同群費用を二重計上しない。N15.02/F03は参照費0、実配賦null。accepted加点未定/自動0、工数率null。実command/対象snapshot/終了code/coverage/証跡hashは結果934へ追記。
