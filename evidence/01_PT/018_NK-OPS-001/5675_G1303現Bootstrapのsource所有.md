# G13.03 BootstrapのsourceとWBS所有

現Core `2611e1acbd`。WBS58原行854、実行635。正本SS361、481、485と保存JARを照合。期待値は全Javaに固有ownerがあり、全物理名がその外側型に結び付くこと。現Gitの入力、JAR中央ディレクトリ、WBS58の検収項目を照合した。

現88ファイル・201物理を9所有へ結合。旧34・117に対して現パス追加54、旧パス変更12、同一22。既存のPG23836によるJDBC二型の所有訂正を追跡した。JAR生成源との差はBootstrapの試験fixture一つで、製品入力は一致する。

PG41432のmanifestと表に個別source blob、物理名、中央CRC、文書・所有・終了依存を記録した。実行 `python3 -B evidence/01_PT/018_NK-OPS-001/input/5675_g1303_current_bootstrap_owner.py`。最終終了0。二つの事前読取条件の誤りを直して再照合した。製品試験、coverage計上、class展開は0。保留のnative一型は名前のみ。個別メソッドのoracle、実環境、全451、正式判定は未成立。
