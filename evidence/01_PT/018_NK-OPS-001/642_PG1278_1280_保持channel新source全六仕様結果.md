# SSC261保持channel故障・新source全六仕様/結果

Program NK-OPS-001/NativeCoveragePrivateFile、WBS-P018-08.01/.02/.03及び必要回帰K01.01。SYS004/OPS009/TST004、UI212/251、SS343/451、SSC261 design-onlyPR100/main00fe3b90d。固定profile/name/path/FD/owner/mode/link/ACL/readonly/SHA/正常close・partial保全は不変更、RD/UI/業務/DIF差分なし。

Source769ddb15cd735c25fef581b5f9850ef9d0053c0f、main製造df2c316e7/NativePrivateFile0897eaf6…。候補未配備、VMはD5/PG1068/BOM0b61を保持。新sourceの実行結果は [公開manifest](evidence/provisional/PG1278-1280-held-channel-fresh-six/manifest.json) に環境/branch/command/source/日時/exit/XML-static-jar-exec/source/log hashとmodule counterを保存。raw exec/session/trace/logはGit外、秘密情報無し。

| Test ID | 事前fixture/入力・操作 | 独立期待値・根拠/実結果 |
|---|---|---|
| PT-OPS-NCHANNEL1278001 | Pin size=-1/0/307842/307844、307843＋readonly false/true、null観測port/観測IO例外 | 固定size307843とreadonly両条件、誤sizeでは観測call0、nullはIA拒否、IO非成功。これはscalar契約でRoot/物理pin authorityではない。全成功 |
| PT-OPS-NCHANNEL1278002 | Package-private資源port null、writer/reader返却null、実held tmpfs inode | 初期nullはcreate0、返却nullはIA拒否・新partial保全、writer-nullサイズ0/reader-null7、全channel/FD返却。NPEを正常化しない。全成功 |
| PT-OPS-NCHANNEL1278003 | Real held Linux FileChannelを保持するfault adapterでwrite/read0、前後size差、3byte-short/8byte-long against7、writer/force/reader/close故障 | 0進捗/不正len/前後size/force-close例外はIO非成功。固定literal7byteはwriter-zero/errorなら空partial、他は全元literal7byte保持、create1/sync0・全owned FD/実delegate閉鎖・caller byte不変。期待値はSS/count/size/literalから作成しProductionhashをexpectedに使わない。全成功 |

既正常6role/new-only/padding/owner-mode-ACL-link/null/unknown・同inode同size変異first/reopen・Root-onlyphase/closingrole不正名・real TERM143/latecapture/stop-owner及び全moduleの既独立期待値を維持。新Default NativeFileCallsは既FileChannel READ/WRITEを保持entryだけに使い、Io観測と資源所有を分離した。SS261 source変更が全六回帰trigger、管理文書だけの不要反復ではない。

選択PG1278は29PT/FES0/bootstrapstatic0/21.768231秒。当fresh全六PG1279はactualexit0、06:46:30.539～07:04:42.839JST/1092.300231秒。同HEAD/allsource-file hashは前後固定、PG1280はGit immutable blob全件・全XML/testcase/FES/flaky/rerun/not-run・mtime・全jar classbyte・全6SpotBugs・session topology/timeを独立照合。3569PT/523suite/1635main class、F/E/S/flaky/rerun0、static6=0、source qualification実0、私有manifest1c21767249100f4716fc9bebb8de86081dca92cf86e5ad9ac158ba457d259e7b。旧6target証跡をpg1279-previous-six-targets-v1へ先保全、旧native/選択execの合算0。

hostのみ残counter=L3794/M632/C40/B1094。共通StopHold単classはL46/M7/C1/B28全miss0、NativeFileCallsはL2/M2/C1全miss0（分岐なし）。NativePrivateFile本体はL30/M10/B1未網羅、主に実Rootの物理pin/default adapterとservice正常出口。型data-only試験で本番Root/Unit/pinを成功にしない。newsource実native/defaultpin/全四100、batch・Log再送/故障/競合、CHR/QA051、正式451/trace/引継ぎは残件。正式PT-WEB-20260925-24/1964PT/53scope、全WBS受入0据置、IT/ST完了ではない。

群見積りは前固定subsetだけ（SSI/O .3/.6/1.2pp、必要K01 .5/1/2pp）。親event0353～0361は書換えず補足0363から子leafへ対応、共有費用の按分・各子予算再加算0、N/Tと個別実費はunknown/null。全6成功はnative・formal・allleaf終了と分離する。
