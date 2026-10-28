# 2491 ProcessResourceScope 現whole7通常PT仕様

2026-10-29、PG-D811予定、主F03・canonical artifact親P01804は参照のみ/追加費用0、START2870/開始0.75/2/4pp/cap10/fresh25残75/reset1793774153。最初のparentをcost leafにした入力はappend前に拒否されevent未登録・製品未起動、今回は主F03単独leafで登録し親を改変していない。source17ab52b253282ce45016f0586c0167a22029fd8c/保存7721271601、normal13596/1f1ff5bbと静的独立13599/ecb27a32は当同sourceの既成功を参照し、確認再演0。

## PT_DEFAULT・全scope

元ProcessResourceScopeTest全552行/七methodと、Main ProcessResourceScope86/SystemctlStateSource151/InspectorUnitProbe372/StopGateException/StopGateFailure/ResourceScope131・Target enum/StateSource interfaceを確認。Test SHA cf94df05fa8559b35af74879256271b41df718f7f5eb1b5251cc0a9f42d99d06は13400/13402の五literal是正前c2a9e98f…から変更済み。元1103/1104/1228/2334/2335の成功/理由を当runへ転用せず、既whole七を一回のみ実行する。

Start portは全て新しいChild/StreamingChild、null返却又はthrow-only lambdaへ明示注入。全Process methodは自己所有fakeのgetters/isAlive/destroy/wait/exit counterとメモリstreamだけで、NativeProcess/ProcessBuilderの既定providerやdefault NativeReader constructor/forTargetを選ばない。command文字列はfakeに渡す値でsystemctl/busctlを起動しない。実OS process/PID/Unit/DB/JMS/FS/native/Root/VM/credential/鍵は操作0。virtual thread二本のbarrier/5秒joinと内部drainは当JVMの自己所有、割込flagは各case finallyで解除。API/Web Graph9/TIE処理へ到達せず、保留wholeからのmethod抽出/別fixture化0。

## Testと独立期待

SS333/SSC063/308、SS341/343/354、OPS009/UI251。元QUERYOWN001..007全methodを保持、新Test ID/JUnit method0。

- 001：normal/IO/interrupt/known-stop/runtime/error×cleanup normal/stop/runtime/error、固定winner `Ncre/bbce/bbce/bbce/bbbb/bbbb` をuse/acquire両modeへ適用。期待はliteral matrix、元例外identity/固定secondary/interrupt flag、factory→body→release列。
- 002：factory IO/runtime/errorは取得前の元identity、null port/null結果はbody/release0。
- 003：同一例外/既suppressedを保持しself-suppressionを避け、固定COMMAND_FAILURE secondaryを追加。
- 004：自己所有二virtual thread/barrierで独立owner、inner→outer解放順とfinally interrupt/join消失。
- 005：Systemctl fake全三getterのnull/throw、三getter後のnull拒否/既取得のみclose・fake destroy1/wait0。
- 006：Inspector injected fakeの通常/streaming両mode全getterの即時null/throw拒否、後続getter未呼出/既取得close・fake destroy1、null Process返却拒否。
- 007：固定ticks/blocked memory drainでwait前0/wait false/非0exit/get前0/get timeout/interrupt、invalid入力はStart0、stdin/stderr/stdout一回close/fake destroy1/割込再設定。sleep/実時間競争で期待を生成しない。

48個のmatrix入力（24×二mode）を48JUnitや新48 Test IDとは数えない。標準whole7 launcherがfound/started/succeeded/unique7・F/E/S/abort0を確認し、失敗/flaky/not-runは合格に算入0。input/expectedは元固定literal/call列/独立nanosから作りProductionでexpected生成0。

13664は既scoped_prometheus_hostの固定SDK/六jar/新only SLOT/clean ENV・公式JUnit/JaCoCo append=falseでwhole7をfresh compile/run。13666は元七XML/実case・全source/SDK/exec/session・同normal class CRCを独立照合する。coverage targetはProcessResourceScope.javaの完全closure（三physical：executable本体1＋自然zeroのQueryWork/OwnedQuery interface2）、手動counter除外追加0。SystemctlStateSource/Inspector NativeReader等は依存として一部実行しても当単位の100%へ算入せず、実OS/native資格とはしない。実missは公開し100%へ補完しない。旧exec/別source counter合算0。

結果2492予定、OS/JDK25.0.4/command/時刻/branch/source/archive/全input/fixture/hash/終了/実counterはmanifestへ。全995旧runtime/原WBS予算受入/正式1964-53/17-190/工数null/QA051final/全actualHOLD/全原本保全は不変更。YKT1819他候補OPEN、残10以下又は枠不明で保全、通常群/報告/commitで停止しない。
