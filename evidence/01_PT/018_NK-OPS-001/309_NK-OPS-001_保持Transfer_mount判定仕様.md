# 309 保持Transfer mount判定（SSC162/BUG519/YKT373）

Program NK-SCN-001/API TransferRootInspection.inspect、LinuxInodeSecurity.readOnlyFilesystem。RD FIL-001～009/OPS-009、UI237/251、SS333 §7.4/343。通常起動・全100%正式認定は別未達のまま。

| Test ID | 条件・入力・操作 | 独立期待値・根拠 | 証跡 |
|---|---|---|---|
| A06-MOUNT001 | 0750実ext4 rootをnative FDで保持。SPIのST_RDONLY=true/falseを各1回観測 | trueはUNAVAILABLE・固定message/causeなし、falseはSDS検査まで成功。能力pathだけを観測、root mode/empty不変。Linux ST_RDONLY bit1とSS333のAPI RW契約 | TransferRootInspectionTest、次選択run |
| A06-MOUNT002 | 保持mount観測失敗/null | 不明はUNAVAILABLE、nullは境界違反、writable path fallbackなし。観測1回/root不変 | 同Test |
| A06-MOUNT003 | 隔離VM/API UID999 GID981+980/982/986、cap0、ProtectSystem=strict/Transfer限定RWのread-only診断 | 保持属性/SDS/ext4合格。Java FileStore readonly=trueでも保持statvfs readonly=false。診断成功はready代用でない | Work PG379/pg424-transfer-inspection-v2-private.log、source修正前実観測 |
| A06-MOUNT004 | 同Source固定全6・署名BOM配備後に外部Morning→通常API | sandbox不変更、TRANSFERを実probe/scanして次境界へ。UP/全終端/cleanupは別実証、client0を合格にしない | 未実行 |

期待値はLinux mount flags/SSから独立作成し、productionでexpectedを生成しない。実負read-only mountの拒否、native statvfs errno/invalid capability/null/ABI境界は既存LinuxInodeSecurityTestと合わせて検証する。source/branch/command/日時/OS/JDK/終了/coverage/BUG・SSC/hashは実行後safe manifestへ固定し、raw path/credential/sessionをGitへ入れない。変更APIの選択回帰後、同起動契約群固定Sourceの全6で既存不足/追加/解消を別記する。現時点未実行を合格にしない。

15:34選択v2：Protocol7/Storage9/Bootstrap7/API21=44PT、FES0/SpotBugs4zero/strict compile/format合格。A06-MOUNT001/002を含むAPI21は当該4classだけで、targetに残る古いsuiteを加算しない。BUG520のAPI単独M2 compile失敗は不算入。工具compile-only annotation漏れ、続くhost tool runtimeでAPI classes漏れ（BUG521/既存BUG513共通原因）はstrict guardで拒否し、完全classpathで再compile/85assert成功。旧世代保全native exit0とA06-MOUNT003のhashは`evidence/provisional/PG425-captured-transfer-boundary/manifest.json`。新SourceのA06-MOUNT004/全6/100%・正式認定は別未実行。
