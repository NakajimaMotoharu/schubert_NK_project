# root検査stream所有の是正・再試験仕様結果

BUG1289/YKT1055、2026-10-15、PT-SCN-008-A07/FILESTREAM1289、Production a9/PG2802不変更。修正前9fb711adbで先行起票、587fba071で既Testへ独立FD後条件だけを追加し、46baa922dでFiles.listをlexical closeへ是正。期待fixture6件・既全3methodを削除/変更せず、Main/設定/署名/配備/VM/既原本操作0。

## 目的・独立oracle

StorageRootInspectionTest.a07の公開temp rootに6個の子directoryを用意し、既Production inspectの全所有close後、fixture rootを指すOS FD数をprocfsのsymlink読取で独立観測する。scanner自身はFiles.newDirectoryStream(/proc/self/fd)をtry-with-resourcesで閉じ、別inodeを指すのでfixture FD数へ混入しない。別FDの観測中消滅だけは対象外とし、本fixtureのbefore/after一致を要求する。Productionのclose methodやreturn値をexpectedへ使わない。FD番号/生環境/秘密を公開しない。

## 実before／失敗／after

| stage・固定Test source | 実際結果・認定範囲 |
|---|---|
| before-v1 /587fba071 | 10:36:52.936251～10:37:04.341815Z、真正Maven1・Test3/1suite/1failure/0error/0skip。失敗はA07のAssertionFailedError `expected0 actual2`のみ。診断wrapper0は「漏れ実証に成功」でありPT合格ではない |
| after-v1 /46baa922d | wrapper1、実163/23・4failure/3error/0skip。observer用umask077がMavenへ継承され通常0640/0750を0600/0700へ縮小。BUG1290/YKT1056先行7f0e49c83、修正d2cf7759c。原XMLとBUILD FAILUREを保存。inner Maven終了codeは分類拒否前に永続化されていないため**独立観測値null**、失敗を成功や未実行へ変更しない |
| after-v2 /d2cf7759c | after-v1と是正Test全byte同一、私有observer077/試験child0027を分離。10:39:20.686476～10:39:40.431494Z、真正Maven0・全Storage163/23/FES-flaky0、独立FD0→0、静的0・LINE1172/METHOD257/CLASS37/BRANCH527全miss0。全Storage74Main/Jar全member/resource/debugが既sourceと同byte |

公開`evidence/provisional/PG3326-stream-lifetime/manifest.json`は別ROで元payload SHA/固定archive/source、各原XML/元manifest/log SHAを照合した。引数値/properties/stdout/privateログ内容は輸出しない。before/failed-after/after-v2のsource/runを別に保持する。Mavencommand・Test/coverage/static/Jar hash・時刻とchild maskは同manifest。JDK25.0.4/Maven3.9.12/aru普通UID、既全3302と同じ0027を使用し、Production mode期待値や本番権限を補修していない。

## 全対象横展開・再発防止

PG3328はsrc全JavaのFiles.list/walk/find/lines **61呼出し**をfile/行/全file SHAと共に列挙。全60既正常箇所は同じ行のtry-resource lexical ownerがあり同原因非該当、当一件も修正後同じ所有形。現在Mainには対象呼出し0、全61がTest/fixture内。公開PG3328 manifestに全件根拠、直接terminal chain・未確認所有0。保守的checkerは同一行で所有を判定できない新記法をMANUAL_REVIEW_REQUIREDとして拒否し、一般Java全資源解析を完了したとは主張しない。純三checkで旧直接count拒否・全4 operation/qualified名受理・同一行の別未close呼出し拒否を確認。実A07のFD後条件が再発防止の動的証拠であり、検索だけを完了根拠にしない。

工具の純五checkは正常163/23、before一失敗の型/ID/FD差、誤失敗/skip/flaky/重複拒否・Maven module指定・private/child mask分離を確認。旧工具v1の失敗・全原byte/秘密保全物はそのまま保持。BUG1290の有限工具scopeは当実163成功と既3302 nonaffected根拠で成立、BUG1289/YKT1055及びP003-05の品質受入は必要全体統合が残る。

## 必要一全体統合（実行中・未合格）

PG3330、固定snapshot29fc0a3f7b14046b8f3a7c20785d5436dca7095e、archive2b6c8fe91e07896b82358ea355e1891d2df9ead68b5e8329d69fd52f3073aa5b。旧3302との差分は当StorageRootInspectionTest一fileのみ、Test件数は3702/542/1643のまま。実exec23236/19:41開始。同job真正終端→3332独立全XML/input/static/member→3334同a9 sealed28全Main/resource/debug/CRC/session資格を確認するまで全体成功/本障害閉鎖/P003-05受入0。旧3702/native28を新Test集合へ改名しない。現時点正式1964PT/53scope・工数null・QA051final保留/全四100未完は維持。
