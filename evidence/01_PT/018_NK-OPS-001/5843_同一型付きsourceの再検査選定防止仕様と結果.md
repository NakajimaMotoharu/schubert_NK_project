# PT-QA-ROSTER001 型付き検査の既済照合

SS354、WBS-G02・F03、BUG-3844／YKT-2998。対象は `static_input_scope.py` の `--source-only` と同一設定ロスターを指定するオプション。現対象の Git blob と承認・保留 scope を先に照合する。書式は `path` と `sha256` を持つTSV。現inventoryの `sha256ByPath` は計画対象の固定ファイルから取得する。 `--prior-source-roster` と `--prior-source-roster-sha256` を併用する。

独立試験は型付き検査済みパス、同名で変更したdigest、新しい名義、全重複、不正digestと重複行、ロスター固定SHA不一致、引数不足、既保留を固定メタデータで判定する。両オプションなしの従来入出力は既試験で維持。別設定・別使用依存への再検査、および正式全体runは従来の通常scopeを使う。

PG45304の工具23件が終了0。現Webの8件で全重複を終了1の固定理由として検出し、未照合の現Caddy型を混ぜると一件だけを未測定と出力する。コンパイラ／解析器と実業務は起動していない。正式受入への加算0。

[工具実行と選定結果](evidence/PG45304-duplicate-typed-source-preflight/manifest.json)
