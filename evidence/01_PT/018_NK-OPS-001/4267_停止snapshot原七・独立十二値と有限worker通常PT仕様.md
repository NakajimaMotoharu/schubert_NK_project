# MaintenanceStopSnapshot whole原7・独立12値と有限worker

NK-OPS-001、P01804、OPS009/UI251253/SS341SSC100126/343354。BUG2866/YKT2387をPG30106へ修正前起票。追加資格 .35/1.05/2.1、上限3pp、原費用/元S/V不変更。

MSTOP001: Test手書きCOLD12行と固定8完全名/順序、cold・failedFailed・固定cg、回転入力同値。返却observedValuesを独立literal12要素（Id/loaded/inactive/dead/空/0/0/system.slice/no/空/空/0）の固定順でassertし返却List書換拒否を追加する。productionのPROPERTIES/encoderからexpectedを生成しない。
002: 全key欠落/重複/未知/区切り不正と終端LFを拒否、原input各byte保持。
003: 全byte位置のcontrol/nonASCII、2048/2049境界/nullとborrowedbyte消去後snapshot保持。
004: 固定配置・状態/numeric域、Job/PID非zeroとnonterminalのquiescent false。quiescentは停止/cleanjournal/Root権限ではない。
005: Invocation正準lower非zero32、timestamp非負u64/上限とoverflow/非正準拒否。
006: unit・timestamp・Invocation・PID各差分のmatches false、null拒否、同値true。
007: 8worker/64独立byteタスクで固定redaction/matches/quiescent、各Future5秒/finallyshutdownNow-await10assert。割込flagをpureparseで消費しない。元全golden/全assertを保持。

Main Snapshot/MaintenanceUnit/StopGateException/StopGateFailure全4physicalと原Test全7。JDK/JSpecify/JUnitだけ、native/Root/Unit/サービス/DB/VM/鍵/permit/FS操作0。sourcebody全4と全Testを先行読取り済み、HOLD試験の抽出や値から権限を作る代替0。GJF→RootNullAway/lintWerror→PMD/CS/SB→個別適用性→preflight→Git固定→whole7一回→別postの全CRC/初期化/単一exec/XML/四counterを確認。未達/失敗は原結果を保持し除外/期待値弱化なし。実行時刻/環境/command/source/終了/input/output/hashは各manifest、結果文書へ一意結合。実JVMCode対JaCoCo既定filter差は分離し、全451/generated-code例外承認・親stop成功・元190正式受入へ転用しない。
