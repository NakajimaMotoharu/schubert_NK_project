# PG517 全終端ISSUEDから単一API退役

NK-OPS-001 / WBS-N10 / PT-OPS-PG517-001～006 / SS343353/SSC205209210211/QA047/BUG817820・YKT586589。Productiona2/PG495/schema028不変更、工具限定assertはProduction PT加点0。

001: PG516正常handoff raw36362db…/complete d160…/wholevendor80a9…/PID1 87ab…/broker1c69…を原byteで固定し、PG505全row/treeとの厳密同値、現在同boot/署名187/currentPG495/元4startup ISSUEDと旧owner消失を確認。初期ISSUEDからderiveしたINVALIDだけを許す。
002: 新M→A→RWbatch/readCommitted/autoCommitfalse/advisory＋独立RO全24/452/十Ref。全10terminalの全18/configをhandoff snapshotと二読比較する。Expiry/Cleanup/Artemisへのstop commandは0、旧未保存receiptを作らない。
003: 全原値/終端再読後、元actual permit/readIssued/data-only ownerでcanonical revokeを一回。独立SS343 literal INVALID vector/current hash・lengthと、current metadataの許可deltaだけを確認する。元permit/owner/marker全byte・metaは不変。
004: 単一API marker限定退役/sync、前exact4→mutation3/4→後exact3。全原本/DB/native/runtime不変、他marker/launch/Pair/start/DB更新0。異常は現phase相関とM/A確認・usable rootのみでAPI隔離、consumed scope再操作0。
005: 実FD/syntheticRoot/tmpfsのISSUED read302・遷移1699故障位置/35102assert、single-marker1304故障/20907assert、vendorPID148assert。新terminal oracle152assertで全10Unit各liveMain/Control/Job/state/foreignIdを拒否、明示stop関数/driver呼出し不在とphase-specific canonicalを確認。正常/境界/null/欠落/異常・owned/negative・故障は独立fixtureによる。
006: DB rollback/close→十Ref逆順/busclose→root/A/Mの新全scope正常帰還と独立peer/lock0。旧PG505親143・PG513/515工具143/closeUNKNOWNは保持し、旧成功で補完しない。

Host command `bash tools/quality/vm/050_s1/pg517_terminal_api_compile_v1.sh` actual0、Werror0/上記限定assert全成功。native command `python3 -B tools/quality/vm/050_s1/pg517_terminal_api_native_v1.py` は別new-only TOOLS pg517-terminal-api-tools-v1/SAVE pg517-terminal-api-recovery-v1で一回のみ。現在未実行、結果/actual/sourcehash/Root後条件/safe manifestを追記する。真正親DONE/native100/CHR/451formal/PGPT全体は未受入。
