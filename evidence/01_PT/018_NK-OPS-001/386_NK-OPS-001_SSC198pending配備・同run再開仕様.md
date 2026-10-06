# SSC198 pending code-only・通常same-run再開の独立仕様

Program NK-OPS-001、operator Pg481PendingDeployment/original/publish/References、Production MorningProcessMain/既SSC114 resume。RD非変更、UI非変更、SS341/343/353 SSC198補足（main38b04dc5）、QA047承認範囲を一般化しない。Production source bab704707b8fd7e0dc7581c4489f0892236efe73、PG479/a1c34cddの同六byte、工具sourceは保存commit別記。

|Test ID|目的・入力・操作|独立期待値・根拠|
|---|---|---|
|BREC198010-H01|fixed activate/null/欠落/未知/余剰引数|activate一個だけ、公開literal7検査、VM権限なし|
|BREC198010-H02|全値snapshot/config approval差分|固定公開metadata/hashfixture、approval正規Root400/単一link/正規byteだけ、親dirmtime/ctime以外不変。DB一列/原本/part/epoch/request/exec/config欠落余剰mode/owner/link改変拒否。AST束縛は固定owner/current/DB appnameだけ、immutable witnesshash一致。38検査、Production oracle呼出しなし|
|BREC198010-N01|新M→A→実DB/advisory71419602→10私有Ref|PG480-v3正常receipt、全18/kernel・元PG478timeout143/Backup0/PID1二job、署名old/new/fullBOM/freeze-ro、完全pending/同INVALID run494/cutoff06:28:43.734078Z、旧24DB/原本Backup/全native/旧request全値一致|
|BREC198010-N02|全native/heap/oldapproval/current/epoch私有archive後、approval/currentのみatomic切替|currentPG479/正規署名a1c・全BOM、旧INVALIDepoch同byte、二RUNNING・dump-only.part・request・全旧原値不変、Unit/SQL/config別file/start/DB updateなし。常用activate/invalidate/empty/DONE/Pair gate呼出し禁止|
|BREC198010-N03|DBrollback/close→Ref解放child0→A/M正常帰還|全後条件再照合・実DBsession/advisory0、全scope正常後のみdurablecomplete。部分publish/close未知はM/A等retainで未合格、旧timeout/closeを成功へ補完しない|
|BREC198010-R01|別新所有でRoot runtime一回用resume固定引数準備|独立signedbase＋既PG477native literalへ --resume 49437eda-1681-43a9-883a-424eb55a6166だけ。Unit/hardening不変更・before-image・一回reload・全実効束縛・全scope正常。旧/未知dropin/agent/UUID/余剰拒否|
|BREC198010-R02|新durableguard/observer・通常same-run start一回|Production beginBackupのみ旧二件ABANDONED化/新二件と旧request私有置換、同activation可能・旧cutoff保持、真正Backup.CONFIG/manifest/Inspector/親RootordinaryAPI保持Web/Caddy/DONE、独立旧cutofforacle/旧part非eligible保持・全保全、元30min/逆順ownedTERM|
|BREC198010-R03|真正全終端後の別M/A/DB/Refでruntime退役|型付きexactsinglefile/sync/reload/readback、既署名base/PG477nativeのnoargs復帰、旧履歴/archive不変|

環境=host/隔離VM JDK25.0.4/Python3.14/guestboot e07aa。command bash tools/quality/vm/050_s1/pg481_pending_compile_v1.sh（v1compile未実装accessor誤記actual1→v2）、python3 -B tools/quality/vm/050_s1/pg481_pending_native_v1.py。ログ/DB/rawheap/credentialはworkPG379/Root私有だけ、Gitは集計/hashのみ。Coverage：工具検査をProductionPTへ算入0、ProductionPG479の3381/508/static6zeroは既結果保持、同source真正native/global100/CHR正式は未達。Failed/skipped/notrunを成功へ加算しない。BUG771/YKT551・BUG544/YKT388継続、結果387へ。
