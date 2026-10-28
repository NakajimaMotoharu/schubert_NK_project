"""Independent four-Test physical/ConstantValue proof bound to corrected same-source static run13216."""
import pg13203_resource_db_literal_config as cfg
import f03_literal_batch_quality as quality
from f03_literal_batch_sources import out as original_out
import g07_host_class_provenance_inputs as data

def qualified_input(context,number):
    # Explicit replacement input reference, not reuse of the failed13210 result.
    if number == context.STATIC_NUMBER:
        assert context is cfg and number == 13210
        return data.BASE/'PG13216-spotbugs-fresh-six-cli-v1'
    return original_out(context,number)

if __name__ == '__main__':
    quality.out = qualified_input
    quality.post(cfg,'6d7f55c22a3ffec8a9013e706282ac845c595492',
        '01df6a3463d330c92815ca7ac11dd27d4eb320d767ee8069ef36898c6506ecd4',
        '3ec8326e0c54daf26b3bc500a7b2ceb62f34abc0a9647c8ed140e9f19708f8c0',
        ('PG13207-resource-db-literal-preflight-recovery-v1','abcff1ed823336314e9f56f1f66cde531a44c6e954d14830738fd511733d4b22'))
