"""New-only current full11/canonical10 evidence; old Root tuple never becomes authority."""
import inspect
import pg3754_current_before_view as previous
from pg3978_current_preservation_readonly import CURRENT, BOM


def role_text(raw):
    for old, new in [('pg3752-current-preservation-readonly-v1', 'pg3978-current-preservation-readonly-v1'),
                     ('pg3754-current-before-view-v1', 'pg3980-current-before-view-v1'),
                     ('pg3754-current-4856-before-view-v1', 'pg3980-current-7fff-before-view-v1'),
                     ('pg3662-native-stop-v1', 'pg3902-native-stop-v1'), ('native34Preserved', 'native46Preserved'),
                     ("==34)", "==46)"), ("'nativePhysicalFilesPreserved':34", "'nativePhysicalFilesPreserved':46")]:
        raw = raw.replace(old, new)
    return raw


GUEST = role_text(previous.GUEST)


def main():
    values = {**previous.__dict__, 'CURRENT': CURRENT, 'BOM': BOM, 'GUEST': GUEST}
    exec(compile(role_text(inspect.getsource(previous.main)), '<new-only current data view>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
