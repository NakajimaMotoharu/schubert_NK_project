# MorningStartupLaunchOwner原whole3仕様

2026-11-01、PG17160-MORNING-LAUNCH-OWNER-ORIGINAL3、WBS-F03、事前正式1/3/6pp/cap10。Source6b固定。新fixture/部分抽出0、元Test114行そのまま3@Testをfresh compileし一つの所有JVMで実行する。

同6b既fullSource post16620-a878d423とstatic review equivalence16617-b7589a46を再利用し、Main SHA caca5ef9とnormal14216を照合。Main全体9physical（Code4/NoCode5）を分母とし、sequence以外未実行は未達のまま。未実行classも黙って除外しない。既scopeのcoverageと合算しない。

READY428007はAPI→WEB→completion、earlier/started immutable、成功時stop0。428008は3段階×IO/Runtime/Errorで元例外同一性と戻りownerだけ逆順stop、独立literal順序を期待値とする。428009は三callback nullとWEB戻りnullを拒否しAPIだけ解放。NPEはnull契約のrejectを期待し正常扱いではない。全Testとsequence477～495・pure interfaces・enum利用・class初期化依存を確認し、String/List/ArrayListのfake callbackだけ、actual launch/stop、Root、clock、IO、DB、鍵、provider変更、Thread/Executorは全0。

SharedSelectedJunitReporter固定c9d94f87を使用し元method名/件数/終了0/FES/aborted/not-run0を照合。fresh append=false JaCoCo session/CRCと全9physical counters、独立oracle/metadata反例を記録する。静的六moduleは元14224の限定Spotbugs0参照のみ、PMD等全F03合格へ昇格しない。四held六native/RootFailed/actual境界にrecord/probeがないことを受動readerで検査する。四100%にならなければ未達のまま。仕様/Source/Test変更なし。結果は3343へ記録する。

