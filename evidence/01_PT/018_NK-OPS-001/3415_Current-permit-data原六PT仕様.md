# 3415 Current permit data原六PT仕様

NK-OPS-001/SYS002004/OPS009/UI212251253/SS341342343§6.15・SSC086～089/PG371/PT-OPS-RPERMIT001..006、PG-D1099予定。Source6b53/normal14216・開始HEADb51e729b124be33c238e5233c9272e91ca950de2、群17640/見積1/3/6共有pp cap10。whole Test128行・Main89行を読取（Main a2b964d8…/Test0c399beb…）。RootServiceLauncher initial state/constructor declarationsと呼出しrun87～106も読取、static initializer無し/runは注入Admissionだけを呼んで正常帰還でも30。constructor/main/preflightを呼ばない。実Root/permit/namespace/鍵/DB/VM/native操作0。

001 WEB Snapshot固定boot1111…/invocation1×32/pid42-start43-parent44とsynthetic Permitのrelease a×64が一致なら受理。002 APIも同相関。003別boot2222…/別release b×64はIOException。004 MORNING/CLEANUP role拒否、snapshot/release/permit nullはNPE、verifyNative(null,...)もreadNative先頭null-rootでIO前拒否。005 permit nullを代用せず、invalid digest形式not-a-sha256はrecord constructor IAE。006注入AtomicInteger callback一回だけ、RootServiceLauncher.run(WEB, callback)が非成功30を返す。

fixture BatchRun/Activation/Permitは公開固定UUID・cutoff2026-09-29Z/固定hex syntax、実署名/認証/発行/consume/revoke/authorityではない。Nativeというmethod名のverifyNative/readNativeはnull guardまで実行するがroot.recheck/LinuxDirectoryCalls/OwnedTransferDirectoryには達しない。IO0をmethod-entry0と誤記しない。並行/再送/所有資源はpure comparison/immutable constructor/null boundary/injected scalar callbackのため当wholeに非該当、外部作用0。expectedはTest literalとcallback countだけでproductionから生成0。

対象Main全二physicalはouter CodeとObserved record Code（未実行も0coveredとして分母）・NoCode0。現16330の完全Sourceproofは保全し、原六はscope-only追加・exec合算/旧成功再演/新Maincredit0。既RootServiceLauncherTest六は3275で現source資格済につき再演0。MaintenanceOwnerFrameTestは3252/3127の明示HOLDを維持・抽出0。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17640_current_permit_data_six_pt_v1.py。固定SDK/六MainJAR/JUnit1.13.4/Java25.0.4/180s/append=false新SLOT、既normal/static/reporterはpin参照し再実行0。postは元XML/FESabort0、単session/CRC/全Source二、四held/六native/RootFailed/Cycle/inactive Root外側の不在を確認。Src/Test/環境/command/exit/期待実値/input/hash/coverageは3416/3417へ。未達/skipped/未知は合格化せず、正式1964/53・新受入0/工数null/QA051final/HOLD不変。
