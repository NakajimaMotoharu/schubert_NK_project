"""Fresh six-artifact complete-class static analysis; no Product Tests or application start."""
import pg13501_main_assignment_config_v2 as cfg
from f03_spotbugs_fresh import stage

if __name__ == '__main__':
    stage(cfg,'df0c755d82564f2a637206a1bda5c33c7df7006c','821f7dee356d4af38311c7cac5f79254e06f6aa8d4d3cf9bfd70e65be018595b',
          ('PG13505-main-assignment-seven-v1','aaa38f93d84f57a9ef670699063e6f290fc863326badd2db9d7a4592730929bf'))
