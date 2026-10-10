# WD-BUG-005 (副担当ローカル、正式915採番待ち)

UI222§5は必須項目labelの「必須」表示、HTML requiredとserver validation併用を要求する。質問textareaはrequiredだがlabelが「質問」だけ。questions/new.html/P016-18に限り可視「必須」文字を補う。body/token/controller等の挙動変更なし。UI224§2の1～4096byte/NFC/改行・末尾space/表示escapeは既存契約を維持し、対象templateの独立fixtureで照合する。
