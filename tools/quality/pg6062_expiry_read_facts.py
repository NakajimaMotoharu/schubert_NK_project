"""Two exact read scopes; compile/invoke parse-only helper,never Production code or PT."""
from pg6046_jdbc_ownership_facts import collect
from pg6054_expiry_read_qualification import SOURCE


if __name__ == '__main__':
    collect({'ExpiryAuditRepository': 2}, SOURCE, 'pg6062-expiry-read-facts-v1')
