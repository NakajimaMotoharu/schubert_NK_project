"""New-only namespace after BUG1551 Test generic compile fix; preserve original v1."""
from types import FunctionType
import pg6140_api_jms_close_selected as profile


def main():
    scope = {**vars(profile), 'SLOT': 'pg6144-api-jms-close-selected-v2'}
    return FunctionType(profile.main.__code__, scope)()


if __name__ == '__main__':
    raise SystemExit(main())
