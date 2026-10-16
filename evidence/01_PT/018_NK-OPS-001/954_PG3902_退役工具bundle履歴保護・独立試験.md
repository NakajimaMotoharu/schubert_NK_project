# PG3902 退役工具bundle履歴保護・独立試験（実退役前）

NK-OPS-001、SS343/353/451、BUG1327/YKT1093、Production7fff/PG3748。新3900のfresh VM/boot/current/runtime read actual0、after **d6551955e6a99da0e1250cb94a932eeabc65d3078ea55edc6371b629fd45a6d8**はexact10。実単一target `zz-pg3844-once-resume.conf` **644byte/SHA bfa7d75b74fccd6a29e319739fded4eabd74647e24e426a7fabb4e108be91cba**。data-only、retire/start/SQL更新0。

| Test ID | 独立入力/期待値 | 結果 |
|---|---|---|
| PT-RUNTIME-IMMUTABLE-BUNDLE-BEFORE | 元pg2050の実seedへ、履歴文字列`pg2030/Pg2030/PG2030`を持つCHAIN固定fixture | 変換後2050へ改変を修正前再現。実DB/現成功証跡の変更0 |
| PT-RUNTIME-IMMUTABLE-BUNDLE-3902 | 名前変更/後続変更/追加helperを通じて7種protected assignmentを退避・一意性/実assignment/原byte確認後に復元 | pure3成功、nested/同値複数/marker衝突・消失・重複・comment化・Java移動・追加authority・不正文/型を負例で拒否 |
| PT-RUNTIME-EXACT-FD-3902 | SSの単一target/hash/644byte・held FD/inode/metadata、unlink/fsync/close、全24/設定/履歴の許可差分 | 独立3実FD試験をpure内で成功、327負例条件・16 IO故障位置、VM0。Productionからexpected生成0 |
| PT-RUNTIME-CLOSURE-3902 | current stopped sourceから17fileを生成、元全protected assignmentとCounter一致、現在Root binding、全11 capture keys、任意履歴のnamespace/finalalias衝突 | pure3成功、最終alias変更も保護中だけ。元単一file API不変更・現3876 pure1成功 |
| PT-RUNTIME-ABI-3904 | 全17実Java/Python closure、lintWerror/独立oracle/label/original | 全四phase0、02:56:42～43Z、operatora531bad96、pg3904-frozen-v1.safe.json |
| PT-RUNTIME-DISPATCH-3906 | stage/retire二操作のみ、new-only予約/actual frozen/current after、別stop-before再照合/strict全post契約 | pure2成功、実stage/retire/postは未発行 |

旧3600→3662と現3876→3902のfrozen pair全fileSHA/全protected assignmentを独立比較（PG379/pg3902-frozen-capsule-crosscheck.safe.json、03:00:56Z）。いずれも現物にprotected assignmentのinline自体が**0件**、したがって旧frozen actualで履歴改変が起きたと主張しない。実DBは実行時読取であり元独立全後条件も保持、旧成果を再実行/改変0。汎用seedへ将来inlineが渡った時の再現可能な欠陥を新経路で保護した。任意の旧工具再実行の安全性を承認するものではない。

3908postの役割変換入力も現時点のprotected assignment無しを確認し、追加された場合はVM操作前に拒否するguard/negativeを追加。RECEIPT等は変換**後**に固定値を注入。新3902/3906/3908の実consumer・正常scope/全原値/native保持が未実施なので、BUG1327/YKT1093全体は未完。

Linux/JDK25.0.4/Python3、完全PYTHONPATHで各`python3 -B tools/quality/<対応test>.py`。全command/exit/hash/時刻/対象sourceをPG379の元manifest/再現JSON/frozenへ保存。FD fixtureは独立一時directory内だけを作成・回収し、実runtime退役を代用しない。生DB/鍵/原本Backup/token/session/native/歴史private snapshotsのGit輸出0。管理pure・工具ABIをProduction3714や正式1964/53へ加算0、coverage100/F03/PGPT/IT/ST完了0。
