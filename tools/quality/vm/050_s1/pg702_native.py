"""Fresh immutable verify followed by one durable existing-only execute."""
from pathlib import Path
from pg702_sources import native

R = Path(__file__).resolve().parent
if __name__ == '__main__':
    exec(compile(native(), str(R / 'pg702_native.py'), 'exec'),
         {'__file__': str(R / 'pg702_native.py'), '__name__': '__main__'})
