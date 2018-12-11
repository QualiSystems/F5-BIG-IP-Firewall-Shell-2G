from cloudshell.devices.standards.firewall.autoload_structure import GenericResource
from cloudshell.devices.standards.firewall.autoload_structure import GenericChassis
from cloudshell.devices.standards.firewall.autoload_structure import GenericPort
from cloudshell.devices.standards.firewall.autoload_structure import GenericPowerPort

from cloudshell.f5.autoload.f5_generic_snmp_autoload import AbstractF5GenericSNMPAutoload


class F5FirewallGenericSNMPAutoload(AbstractF5GenericSNMPAutoload):
    @property
    def root_model_class(self):
        return GenericResource

    @property
    def chassis_model_class(self):
        return GenericChassis

    @property
    def port_model_class(self):
        return GenericPort

    @property
    def power_port_model_class(self):
        return GenericPowerPort
