"""Same current862 ABI, separate new885-only frozen stop payload."""
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
 raw=(R/'pg877_compile.py').read_text().replace('Pg877','Pg887').replace('pg877','pg887').replace('pg875','pg885').replace('pg876','pg884')
 return raw
if __name__=='__main__':exec(compile(source(),'<887 second true-cohort Werror>', 'exec'),{'__file__':str(R/'pg887_compile.py'),'__name__':'__main__'})
