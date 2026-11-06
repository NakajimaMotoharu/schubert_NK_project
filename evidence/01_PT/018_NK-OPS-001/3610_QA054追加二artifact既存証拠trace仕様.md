# QA054追加二artifact・既存証拠trace仕様

主WBS-G13.07、開始.25/1/3pp・cap4。source-ownerはCorrelatedLogEvidenceValidator=P02001、WebHttpLogKind=P00603。PG21766/21768の追加二項目に、QA054/UIC011/SSC336・UI235/264・SS312351355・RD FUN002/FUN008/MON003/TST004の既存要求と独立期待を結合する。過去実費を変更せず追加製造費0。

原015044/045・PG19558は新5＋関連10=15、原020001/016/017・PG19608は新7＋関連9=16で、それぞれ別source・一execの真正成功。両Main sourceとphysical byteがcurrent normal20990/21088と一致する場合だけ、当二artifactに過去の有限証明を参照する。新sourceの全体runや31件の新規実行とは表さない。元15branch未達のPG19588と原失敗群は保持し、旧exec合成を行わない。

PT-OPS-QA054-TRACE001（metadata）: 元manifest/coverage.xml/公開case XML/begin/終了記録のhash・F/E/S/aborted0を照合する。Test source/Git/input hash、独立literal期待の原015044/020001016、元selected class/methodの全15/16件を固定する。current Main SHAとnormal class SHAを一致させる。再Unit/compile/report/JVM/実capture/DB/Browser/Root/native操作なし。

PT-OPS-QA054-TRACE002（metadata）: coverage.xmlの当2classの全6/17methodとdescriptor/各counterを残し、独立仕様のTest ID集合へ結合する。Web kindの定数/metadataはMENU002、eligibleの条件/nullはMENU001/002で照合。validatorはschema/相関/閉field/欠落/重複/保持行/数値境界/限定ACTIONの全16IDを一つの実行集合として各methodに結合する。各helperをどの単一caseがhitしたかの個別実測は存在しないので、suite集合内の少なくとも一つが実行したという範囲に限る。実行集合とmethod counterの結合を単一caseのprobe attributionと偽称しない。

全2artifactのbyte/23method/case集合のtraceだけを補い、全G13/全method-assertion trace/全F03/451・WBS leaf受入は未完。新Product method/source証明/実行PT/受入0、正式1964/53・工数率null維持。不一致や未記載Test IDがあれば未確認で保存し、確認目的の再実行へ進まない。
