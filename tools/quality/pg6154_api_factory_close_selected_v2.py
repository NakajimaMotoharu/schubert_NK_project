"""New-only combined ordinary PT after BUG1555 fixture warning fix, no v1 replay."""
from types import FunctionType
import pg6150_api_factory_close_selected as profile


def main():
    scope = {**vars(profile), 'SLOT': 'pg6154-api-factory-close-selected-v2'}
    return FunctionType(profile.main.__code__, scope)()


if __name__ == '__main__':
    raise SystemExit(main())
