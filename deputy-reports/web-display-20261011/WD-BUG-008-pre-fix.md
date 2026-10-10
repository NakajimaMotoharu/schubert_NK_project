# WD-BUG-008 (副担当ローカル、正式915採番待ち)

UI224§5/SS313§6.2はRECEIVEDだけ取消buttonを表示する。templateの条件はaction!=nullだけで状態条件がない。controllerが通常actionを制限する責務は維持し、templateも閉stateを明示照合する。確認labelに必須文字/id/forがなく、operation error summaryにanchorがないUI222/SS313不一致もこの画面固有契約で補う。RECEIVEDと4非RECEIVEDを独立閉fixtureで照合。API所有者/state CAS/再送/operation token発行へ介入しない。client-disabled追加JSは許可外の未達として残す。
