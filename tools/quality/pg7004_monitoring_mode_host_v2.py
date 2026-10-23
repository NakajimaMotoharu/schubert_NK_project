"""New source/new slot after BUG1645; old format failure remains immutable."""
import pg7000_monitoring_mode_host as runner


if __name__ == '__main__':
    runner.SLOT = runner.host.W/'pg7004-monitoring-mode-host-v2'
    runner.main()
