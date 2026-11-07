# 旧package compilerと残二十七型出力の適用

BUG2474/YKT2212、3731/32/PG23194/23200/23202/23204後続。残27のcurrent source pinを持つ旧六module package compiler PG10024だけを代表として、公開manifest/terminal/pomPreflightから実compile処理と保存出力候補を確認する。package/skipTestsは原Unit未実行を意味しても、Test compileの有無を単独で確定しない。

既jar pathからMaven標準target/test-classesを候補として求める際は、compiler-owned host snapshot内・private/guest/archive外・helper FQN prefix/保護name除外をIO前に確認する。原source archiveやSnapshot内protected Java sourceを読まない。現helper source hashとsaved compile source pinが一致するものだけ、そのhelper classfileの存在/header/現在hashを受動観測。元class digestが記録されていなければ「原compile時byte同一未証明」を明示し、新PT/coverage/正式Source資格へ転用しない。

存在しない/変化/不明を元試験失敗や未実装に読み替えず、再package/compile/Unit/field initializer/OOM/VM/DB/Root/実process/私有rawへの操作0を守る。全957Source再parse/8242manifest再索引や元成功Unit/Main静的/covの再演なし。必要な次のtyped metadata/静的範囲は実証から限定する。

着手見積0.5/2/5pp、cap7。追加品質の証拠適用確認。新unique/whole/leaf0、442/whole94/正式1964-53/工数null・全HOLD維持。検証command/SDK/branch/HEAD/対象helper/hash/元compiler/観測結果/未証明事項をmanifestへ、旧原証拠は上書きしない。
