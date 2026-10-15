# typed inode fixture修正と関連PTの実結果

仕様933/BUG1312/YKT1078。元Main4856/PG3420不変更、前像工具/三項式fixturea0df1e96をJava25.0.4で実行（2026-10-15T21:29:20Z/exit0）。uid/gid/modeのexpected Integerに対しactual Longが3件、nlinkは既上書きInteger、dev/ino/sizeはLongで一致。元Test不変更の修正前再現をprivate PG379/pg3678-numeric-conditional-before-v1へ保持した。

0eda98166のPG3680元33計画は27件/5suiteまで成功、batch test compileで追加fixtureの広いIOException宣言がSPIのStorageIoExceptionに不適合となり終了1。元source/archive/log/exit1は保持し、全33合格や未実行6件の成功へ変換しない。新Testの初回compile失敗として計測へ記録、元不具合のbefore証拠と混同しない。

修正e72911c2c、原SPIに合わせStorageIoException.Reason.UNAVAILABLEを注入。新PG3682は**未実行batch6件/1suiteのみ**、Java25/Maven3.9.12/同固定設定、2026-10-15T21:35:35.693288～21:36:19.864494Z、Maven/collector終了0、F/E/S/flaky/notrun0。成功済27件は再実行しない。offline cacheのprotocol/storage/bootstrap各Jarは事前に真正3412の全member/class/resource/debug byteと一致を検証、batch568Mainも全member不変。

checkedAttributesは23/23LINE・1/1METHOD・46/46BRANCH、期待は独立Unix typed literal。正当directory/file/symlinkのリンク数/size端点、Integer/Long型保持・値違反、ACL到達回数/非到達、公開StorageIoException同一identity・null境界の意味あるassertを確認。新2methodは1JUnitずつで、subcase数をPTへ水増ししない。global四100や新全体3714件をこの関連6件から算術認定しない。

実command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg3682_typed_inode_batch_corrected.py`。元Maven argv/XML hash/静的selected batch0/coverage hash/actualsource/時刻は公開PG3684-typed-inode-boundary-v1/manifest.jsonへ接続。原server manifest868f3297c2bd6edda6caf51c5e91e49b05eec44b6b715e56d80158ddcc3b8475、元XMLa7cdc45b306333d0cf011243dbe4261e4911d8323c2a0c950cefaf836951433f、rawログはprivateのみ。

YKT1078の同形検索は一箇所、元missing/String型反例は保持、現fixtureでは全型を独立assertし値条件まで到達、関連再試験成功。修正済/関連確認済、必要な後続全体回帰と同Main native資格は未完。正式1964/53・個別17/190・工数null・QA051final・F03未受入を維持。次は残品質変更をまとめてから必要な一新全体を行う。
