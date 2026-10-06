# PG483 API readiness・配備物negative限定結果

390のHEALTH001～003/FULLBOM011～013、PG-D389。sourceはHEAD3b2588d3da6a29a37194de5f13c901611662b63f＋保存済みsrc差分（固定commit後の全回帰/native未受入）。host Linux/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15、dev-foundation。

初回v1/session49273：Maven BUILD SUCCESS/86PT12suite/FES0/static4zeroの後、終了保存行誤りでwrapper actual1（BUG783）。初回log/差分/started/Maven.exit0/誤redirectをWorkPG379私有保存し、wrapper成功へ加算しない。

再試験 `bash tools/quality/vm/050_s1/pg483_api_bom_selected_v2.sh`、session35937、2026-10-06 19:02:00.576653384～19:03:34.406787377 JST、wrapper actual0/Maven0、fresh clean/Spotless check/NullAway Werror/SpotBugs四module0。XMLはProtocol7/1suite・Storage8/1・Bootstrap40/5・API31/5、合計86PT12suite/F/E/S0。log SHA256 `7eba39ff81106f9615592a96706f3609d7616656376e1c7fd23df509c43b3ac5`、private stem `/home/mini/codex/project1/work/pgpt-runs/PG379/pg483-api-bom-selected-v2`。wrapperにcompleted/source差分が別fileで保存され、BUG783の他shell同pattern検索0、単一対象の修正・字句検査とfresh再試験完了。Production/VM起動変更はない。

HEALTH001：手書きmanagement8通り/consumer4通り、factory sampling0、全短絡順序一致。HEALTH002：同supplierのpublish/outbox故障/stop時の再読取、成功cache0。HEALTH003：依存null各5・Error/LinkageError全supplier位置/Runtime同一Throwable伝播。新factory2とlambda2のline/method/branch missed0、coverage除外0。実Unitの管理200/ready promote/所有閉鎖ではない。

FULLBOM011：Class-Path6拒否/悪性ZIP5拒否/空ZIP拒否/manifest無しclasspath・module-info/dir許可、独立literal bytesを使用。FULLBOM012：14種channel契約故障/null/open/close、意図したVERSION到達1・close一回（open拒否は0）・全FD解放、秘密原因非公開。FULLBOM013：null/foreign parent/duplicate entry拒否、stream close1/全FD解放。ReleasePayloadVerificationは全line/method/class missed0、branch残16（旧同bab full+native残34に対する改善は限定比較、正式source混合0）。src期待値変更・権限緩和・production methodによるexpected生成0。

正式run24/1964PT53scope/48.3%、全coverage100/全scope同source/native/全CHRは未閉鎖。旧PG482同bab10nativeは歴史証跡として保全し、変更後ApiProcessMainへ流用しない。BUG783修正commitは本結果保存commitからGit履歴で追跡、完了日2026-10-06。後続変更群を固定してfresh全6・署名・保全配備・真正実経路へ継続する。
