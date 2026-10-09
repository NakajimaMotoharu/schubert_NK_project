"""New-only prior ended-after-historical-SKIP independent byte boundary."""
from pathlib import Path
R=Path(__file__).resolve().parent
if __name__=='__main__':
    raw=(R/'pg854_completed_reference_selected_v2.py').read_text().replace('pg854-completed-reference-selected-v2','pg854-completed-reference-selected-v4').replace('PG854-completed-reference-selected-v2','PG854-completed-reference-selected-v4')
    exec(compile(raw,'<854v4 fixed source prior time boundary>', 'exec'),{'__file__':str(R/'pg854_completed_reference_selected_v4.py'),'__name__':'__main__'})
