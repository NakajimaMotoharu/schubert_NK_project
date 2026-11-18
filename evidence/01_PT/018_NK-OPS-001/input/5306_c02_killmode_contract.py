"""Validate local KillMode declarations while preserving unobserved effective policy."""


def validate_shutdown_text(configurations, unit_text):
    parse = unit_text['parse']
    one = unit_text['one']
    require = unit_text['require']
    results = {}
    for name in ('ART', 'START', 'BACKUP', 'CLEANUP', 'EXPIRY', 'INBOX', 'API', 'WEB'):
        unit = unit_text[name]
        value = one(parse(configurations[unit]), 'Service', 'KillMode')
        if name in ('API', 'WEB'):
            require(value is None or value == 'control-group', 'KILLMODE_INVALID_OVERRIDE')
        else:
            require(value == 'control-group', 'KILLMODE_EXPLICIT_REQUIRED')
        results[unit] = 'INHERITED_EFFECTIVE_UNOBSERVED' if value is None else value
    return results
