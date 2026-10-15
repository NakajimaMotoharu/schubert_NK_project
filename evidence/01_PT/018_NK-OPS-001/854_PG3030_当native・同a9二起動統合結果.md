# 854 当nativeと同一a9二起動の独立統合

Program NK-OPS-001、PT-OPS-3030-001/3032-001、WBS-N15.01～.06・K01.01。SS343/353/354、451を維持する。Production a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25/PG2802/BOM37bf、guest boot79a。Java25.0.4・Maven3.9.12・Linux aru、dev-foundation。正式1964PT/53scope、工数完成率null、QA051 final保留は不変更。

## 入力・独立oracle

新3026/3028のsnapshot b1a2044f748757bc816e5d9ba877aa94d2864ae2、全3685PT/542suite/1643Main/FES-flaky-notRun0/静的六module0。3022で当activation0ac69のPID1実窓を独立捕捉した10pointを3030が実取得し、各SHA/長さ・session一意性/時間窓・JaCoCo CRCを検証する。Inspector terminal→closingは同session/probe単調性を確認し最新closingだけを使用する。期待値はPID1/固定fixture/byte-map/CRC/session oracleでありProductionの処理結果から生成しない。

3030 actualExit0、最新9stream・10point、Main1643およびresource/META79の全member byte同一、classByteMismatch0。server manifest SHA256=`53be6798d137f3d5297451da9f066c2124854335b10db28ff111461d1d9f571c`。当warm分だけの残数は1003L/195M/8C/536Bであり、先のnoargs分を暗黙に含めない。

3032は同a9の先のactivation747資格済2934 capsule（manifest43ac98d6）と当3030 capsuleだけを使用する。両10pointの個別CRC/session/窓を再検証し各最新9streamだけを18個の相異なるsessionとして統合する。全1643Mainと79resource/METAを新3685のjar全memberに対して比較し、resource一件欠落/余分/改変・class改変を独立反例で拒否する。未知source042/0fd、無資格exec、旧host試験結果の合算は禁止。古いfull3684のexecを新3685へ足さず、新3685の六module execだけをhost分として使用する。

3032 actualExit0、全1643Main/79resource一致、native二activation/20point/最新18stream/独立session18、classByteMismatch0、VM操作0、coverage100=false。server manifest SHA256=`4438443f8d1757c2737747b4309408f76716c95fb361ba817795d0d50fd9c587`。残counterは662 LINE/133 METHOD/5 CLASS/500 BRANCH。旧2934時点835/159/9/513からの差は173L/26M/4C/13Bだが、Test追加とwarm実経路の両効果を含む技術測定であり工数完成率やleaf受入への換算はしない。

## 実行・証跡

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<既記録pyflakes runtime> python3 -B tools/quality/pg3030_current_resume_native_qualified.py`、続いて`pg3032_same_a9_two_activation_join_test.py`、`pg3032_same_a9_two_activation_join.py`。3030 exec24726/3032 exec87964はいずれも真正終了0。工具固定commit6341699f1、src/Main/Test/settingsは新全体snapshotから不変更。純工具1試験はProduction試験数へ加算しない。

私有原証跡はPG379/pg3030-current-resume-native-qualified-v1、pg3032-same-a9-two-activation-join-v1のinput/manifest/logとaru同名PG3030-native-v1/PG3032-native-join-v1。公開するのはhash・非機密counter・追跡IDだけで、exec/session/rawDB/鍵/資格情報はGit非格納。全coverage100/残native経路/CHR/451/trace/個別leaf終了依存は未完。runtime退役は別853の一回操作・独立postで検証する。
