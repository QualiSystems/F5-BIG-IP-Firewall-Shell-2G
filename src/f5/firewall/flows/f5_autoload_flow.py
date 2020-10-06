from cloudshell.f5.flows.f5_autoload_flow import AbstractF5SnmpAutoloadFlow

from f5.firewall.autoload.f5_generic_snmp_autoload import F5FirewallGenericSNMPAutoload


class F5FirewallSnmpAutoloadFlow(AbstractF5SnmpAutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        with self._snmp_handler.get_snmp_service() as snmp_service:
            f5_snmp_autoload = F5FirewallGenericSNMPAutoload(
                snmp_service, shell_name, shell_type, resource_name, self._logger
            )
            return f5_snmp_autoload.discover(supported_os)
