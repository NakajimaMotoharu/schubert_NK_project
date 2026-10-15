# typed inode fixtureと値境界の独立試験

Program NK-OPS-001、RootServiceExecutableAdmission.checkedAttributes・RootServiceExecutableAdmissionTest、SS343/SSC137/143、BUG1312/YKT1078、PT-ROOTELF-3678-001～003。Java25/PT host隔離、実VM・Root・ADMIN操作なし、Main/source4856は保持。

001：現行Testの混在wrapper三項式をJava25で実評価し、Integerを意図したuid/gid/modeがLongとなる修正前再現を保存する。既成功PTの再実行ではなくfixture不具合の独立反例。002：明示Object分岐にして全fixture実classがliteral期待Integer/Longに一致することを先にassertし、値不正をIOExceptionとして拒否。003：root uid/gid=0、directory040755/nlink>=2、file0100755/symlink0120777/nlink1、dev/ino非0、size>=0/file1～8388608、FileTime二項、非symlink ACL空の独立Unix literal仕様を許可/境界/型/欠落/null/ACL例外で確認。値やexpectedをProduction methodから生成しない。

型・値不正はACL取得前拒否、symlinkはACL呼出し0、正当file/directoryは一回/引数44を別counterで確認。元型不正反例も残す。関連固定snapshot Mavenで実Test ID/XML/FES0/format/lint/NullAway/SpotBugsと当method branchを評価する。coverage未達は未達で記録し、人工reflection/除外なし。残5匿名classは実Root/nativeが必要な旧entryであり、coverage目的だけの新業務起動は行わない。まず意味あるhost boundary群を進め、必要な同Main全回帰とnative再資格は群をまとめて実施する。

費用は487 group開始値を参照、今回群subset低0.3/標準1/高3共有ppを一段階・一回だけ保持。485の主担当親P018-03のうち、484の実作業leaf **P018-03.02（欠落/破損/失効/異owner・FD例外の未網羅限定PT）**へ対応する。初期0937のN15.02、次0938の親のみ表記は追補event0949で子criteria/TestID/source/hashまで訂正した。対象はRoot executableのtyped inode/ACL拒否に限り、.02全artifact・依存.01・全体品質を満たした認定ではない。親rollup/.01対象参照/.03終了trace/N15.02/F03は追加費0、個別実費null。元event/見積/compile失敗1と成功27→未実行6の限定成功を不変更、再確認に新製造成果加点0。実証Source4856/Test snapshote72911c2c・XMLa7cdc45b/公開f3a337e4を結果934へ結合。候補5224は未全体検証、旧sourceの関連成功を輸入しない。
