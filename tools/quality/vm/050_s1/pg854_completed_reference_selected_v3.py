"""New-only final affected selection after real pending/foreign-cutoff negatives."""
from pathlib import Path
R=Path(__file__).resolve().parent
if __name__=='__main__':
    raw=(R/'pg854_completed_reference_selected_v2.py').read_text().replace('pg854-completed-reference-selected-v2','pg854-completed-reference-selected-v3').replace('PG854-completed-reference-selected-v2','PG854-completed-reference-selected-v3')
    exec(compile(raw,'<854v3 fixed current source>', 'exec'),{'__file__':str(R/'pg854_completed_reference_selected_v3.py'),'__name__':'__main__'})
