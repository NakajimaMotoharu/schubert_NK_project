# Music階層原Template6仕様

2026-10-30/source6b53/normal14216、主P016-11/関連P016-12追加0、凍結1/4/8pp。SCR011/012/FUN007/UI222/223/235/SS313/323/352、PT-SCR066～071。元MusicHierarchyTemplateTest全369行/6method、必要Main二ViewModel/TopBar/SessionPrincipal/AuthenticationContext/生成wire値/明示MVC構成とbean constructor、二template/layout/CSSを読了。Mock request/responseと明示WebMvcConfigurationだけ、production bootstrap/security filter/実HTTP接続/認証/鍵/DB/再生なし。

|ID|独立期待・fixture・操作|
|---|---|
|066|USER/ADMIN両方、固定3categoryの入力順/総129曲、明示UTF-8 URL、role/navigation/共通CSRF|
|067|同2role、3section/29曲/入力順、明示日本語URL/navigation|
|068|空0件/0曲とcategory20×999999=19999980、section100×999999=99999900、先頭末尾の順/URL|
|069|固定`<b>&`/公開合成CSRFをDOM textとして保持、要素/イベント属性が増えない、明示encoded URL、合成64aの非表示|
|070|許可view2/未知・相対・redirect view3を拒否、固定CSSルール6・二templateのscript/style不在|
|071|own8threads/64render、入力nの名称/件数/URL/actor/CSRFが混線しない、各Future10秒、context/pool close|

期待は入力literal/独立算術/URL literal/DOM回数から算出、productionをexpected生成へ使わない。null/未知view・空・境界を含むが、既Java全Sourceのnull異常branchをこの画面Testだけで全網羅としない。再送/transaction/actualBrowser/ログインはこの局所template対象外、通常PG/PTの別criteriaのまま。

四Main資源はnormal input/snapshot/Jar/現byteを一致、原Test無改変。Files.readString用CSS/二HTMLだけ同byteで新ownSLOTへコピーし、own target固定公開traceだけ生成する。Node/Browserは起動しない。PG14790原6/1 FES/flaky/not-run0、PG14792は独立XML/resource/原ENV/trace/hash/一exec確認。既ViewModel/WebMvcConfiguration資格は不変更、今回新Java Main資格/coverage加算0、resource coverageの捏造0。

command `env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14790_music_hierarchy_template_six_pt.py`。2772結果へ真正終了/日時/command/環境/branch/commit/source/全inputhash/XML/trace/関連BUGを結合。正式1964/53・工数null/QA051final/全HOLD不変。
