"""Fresh same-source six Main SpotBugs; no stale snapshot dependencies, Product PT0."""
import pg13223_db_web_literal_config as cfg
from f03_spotbugs_fresh import stage

if __name__ == '__main__':
    stage(cfg,'1762d68747c3460afd90a03377858572dfc25931','3919599fe1f9798297a75b209802f656f3af603af3ed0df21f114e1dc0c39e74',
        ('PG13226-db-web-literal-v1','f27a3f8cb48dd642c6c125355b7a34db2eac4b4b8ef98654fef9df7a6ba4c729'))
