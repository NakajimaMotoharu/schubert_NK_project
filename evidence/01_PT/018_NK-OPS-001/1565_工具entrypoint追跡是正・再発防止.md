# 1565 工具entrypoint追跡是正・再発防止

実証追加：PG7076-invocation-history-audit-v1/manifest.json SHA `09417ed5a8f46d49d1cd8b04d26df5703af7f5b7906ce052002a8aa5503b6c2a`。元公開35recordのpath/hashとPython入口欠測を変更せず索引化し、過去argvを復元した実測へしない。当7068/7070の実入口/loaded全公開toolを元manifestから照合、helper自己所有fixture4＋六libraryへのcapture/verify/binding順序の正負AST3、計7管理試験0を真正stdout/stderrとsourcehashで保存。任意CLI値保存0、工具途中mutation拒否の再発防止を含む。Production PTへ加算0、元成功再演0。7036の旧設定PTは再演せず共通helperの同byte・六library構造検証で変更範囲の適用を確認し、歴史の実argv欠測は保持する。

2026-10-23、BUG1648/YKT1401。新helper `host_tool_invocation.capture/verify`。変更前の六libraryは実child commandを記録する一方、Python wrapperと再利用libraryの区別が不足していた。元manifestは改変せず、歴史recordの固定commandはlibrary既定の説明であり実argv観測ではないことを1564と後続の索引へ追記する。現在のwrapperから過去の実argv/hashを推測補填しない。

是正対象は7006(host)/7008(post)/7030(六compile)/7032(実Jar post)/7036(設定host)/6990(公開scan)の六library。全派生入口は共通capture/verifyを使用する。7042/7052等の単独入口は既commandと__file__がその入口に一致するためlibrary既定名の誤表示では非該当（実orig_argvを歴史採取したという保証は元々なし）。7066はconfigureを切り出し、新7070が正確な同70対象を使う。既runを再起動0。

新helperは公開tools/quality内のcanonical regular .pyだけを許可し、argvは入口一つ・orig_argvはordinary python3 [-B] 入口だけ。追加引数/別interpreter/不整合、repo外/symlink/非Python/不存在は固定拒否、任意のCLI値は記録しない。entrypointとlibrary/hash、helper/hash、loaded project Python全hashを別記録し、終了時verifyで同byteを要求する。VM/process target/DB/raw/鍵へアクセスしない。

2026-10-23の `python3 -B -m unittest host_tool_invocation_test -v` は自己所有TemporaryDirectory fixtureの正負4管理試験、全0を観測済み（PGPT Production PTへ加算0）。正例二flags/入口-library別hash、余分引数・曖昧interpreter拒否、scope外・symlink等拒否、途中の工具mutation拒否。pyflakes当11file0。raw実行manifest・新host/postのentrypoint適用・歴史索引の保存は後続へ。完了前のBUG/YKT閉鎖0、元/v4/v5見積/元70の結果を変更0。
