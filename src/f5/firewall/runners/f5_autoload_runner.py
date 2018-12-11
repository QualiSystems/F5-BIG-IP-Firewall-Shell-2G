from cloudshell.f5.runners.f5_autoload_runner import AbstractF5AutoloadRunner

from f5.firewall.flows.f5_autoload_flow import F5FirewallSnmpAutoloadFlow


class F5FirewallAutoloadRunner(AbstractF5AutoloadRunner):
    @property
    def autoload_flow(self):
        return F5FirewallSnmpAutoloadFlow(self.snmp_handler, self._logger)
