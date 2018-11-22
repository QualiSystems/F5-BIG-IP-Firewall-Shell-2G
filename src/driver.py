from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.devices.driver_helper import get_logger_with_thread_id
from cloudshell.devices.driver_helper import get_api
from cloudshell.devices.driver_helper import get_cli
from cloudshell.devices.driver_helper import parse_custom_commands
from cloudshell.devices.standards.firewall.configuration_attributes_structure import create_firewall_resource_from_context
from cloudshell.firewall.firewall_resource_driver_interface import FirewallResourceDriverInterface
from cloudshell.shell.core.driver_utils import GlobalLock
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface


from f5.cli.f5_cli_handler import F5CliHandler
from f5.snmp.f5_snmp_handler import F5SnmpHandler
from f5.runners.f5_autoload_runner import F5AutoloadRunner


class F5BigIPFirewallShell2GDriver(ResourceDriverInterface, FirewallResourceDriverInterface, GlobalLock):
    SUPPORTED_OS = ["BIG[ -]?IP"]
    SHELL_NAME = "F5 BigIp Firewall Shell 2G"

    def __init__(self):
        super(F5BigIPFirewallShell2GDriver, self).__init__()
        self._cli = None

    def initialize(self, context):
        """Initialize the driver session

        :param InitCommandContext context: the context the command runs on
        :rtype: str
        """
        resource_config = create_firewall_resource_from_context(self.SHELL_NAME, self.SUPPORTED_OS, context)
        session_pool_size = int(resource_config.sessions_concurrency_limit)
        self._cli = get_cli(session_pool_size)
        return 'Finished initializing'

    @GlobalLock.lock
    def get_inventory(self, context):
        """Discovers the resource structure and attributes.

        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource
        :rtype: AutoLoadDetails
        """
        logger = get_logger_with_thread_id(context)
        logger.info("Autoload command started")

        with ErrorHandlingContext(logger):
            resource_config = create_firewall_resource_from_context(self.SHELL_NAME, self.SUPPORTED_OS, context)
            cs_api = get_api(context)

            cli_handler = F5CliHandler(self._cli, resource_config, logger, cs_api)
            snmp_handler = F5SnmpHandler(resource_config, logger, cs_api, cli_handler)

            autoload_operations = F5AutoloadRunner(logger=logger,
                                                   resource_config=resource_config,
                                                   snmp_handler=snmp_handler)

            autoload_details = autoload_operations.discover()
            logger.info("Autoload command completed")

            return autoload_details

    @GlobalLock.lock
    def restore(self, context, path, configuration_type, restore_method):
        """Restores a configuration file

        :param ResourceCommandContext context: The context object for the command with resource and
            reservation info
        :param str path: The path to the configuration file, including the configuration file name
        :param str restore_method: Determines whether the restore should append or override the
            current configuration
        :param str configuration_type: Specify whether the file should update the startup or
            running config
        """
        pass

    def save(self, context, folder_path, configuration_type):
        """Save a configuration file to the provided destination

        :param ResourceCommandContext context: The context object for the command with resource and
            reservation info
        :param str folder_path: The path to the folder in which the configuration file will be saved
        :param str configuration_type: startup or running config
        :return The configuration file name
        :rtype: str
        """
        pass

    @GlobalLock.lock
    def load_firmware(self, context, path):
        """Upload and updates firmware on the resource

        :param ResourceCommandContext context: The context object for the command with resource and
            reservation info
        :param str path: path to tftp server where firmware file is stored
        """
        pass

    def run_custom_command(self, context, custom_command):
        """Executes a custom command on the device

        :param ResourceCommandContext context: The context object for the command with resource and
            reservation info
        :param str custom_command: The command to run
        :return: the command result text
        :rtype: str
        """

        pass

    def run_custom_config_command(self, context, custom_command):
        """Executes a custom command on the device in configuration mode

        :param ResourceCommandContext context: The context object for the command with resource and
            reservation info
        :param str custom_command: The command to run
        :return: the command result text
        :rtype: str
        """

        pass

    def shutdown(self, context):
        """Sends a graceful shutdown to the device

        :param ResourceCommandContext context: The context object for the command with resource and
            reservation info
        """
        pass

    def orchestration_save(self, context, mode, custom_params):
        """Saves the Shell state and returns a description of the saved artifacts and information
        This command is intended for API use only by sandbox orchestration scripts to implement
        a save and restore workflow

        :param ResourceCommandContext context: the context object containing resource and
            reservation info
        :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
        :param str custom_params: Set of custom parameters for the save operation
        :return: SavedResults serialized as JSON
        :rtype: OrchestrationSaveResult
        """
        pass

    def orchestration_restore(self, context, saved_artifact_info, custom_params):
        """Restores a saved artifact previously saved by this Shell driver using the
            orchestration_save function
        :param ResourceCommandContext context: The context object for the command with resource and
            reservation info
        :param str saved_artifact_info: A JSON string representing the state to restore including
            saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        """
        pass

    def health_check(self, context):
        """Checks if the device is up and connectable

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource
            Attributes inside
        :return: Success or fail message
        :rtype: str
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass


if __name__ == "__main__":
    import mock
    from cloudshell.shell.core.driver_context import ResourceCommandContext, ResourceContextDetails, ReservationContextDetails

    address = "192.168.42.202"
    user = "root"
    password = "admin"
    cs_address = "192.168.85.18"

    auth_key = 'h8WRxvHoWkmH8rLQz+Z/pg=='
    api_port = 8029

    context = ResourceCommandContext(*(None, ) * 4)
    context.resource = ResourceContextDetails(*(None, ) * 13)
    context.resource.name = 'F5 BIG-IP Firewall 2G'
    context.resource.fullname = 'F5 BIG-IP Firewall 2G'
    context.reservation = ReservationContextDetails(*(None, ) * 7)
    context.reservation.reservation_id = '0cc17f8c-75ba-495f-aeb5-df5f0f9a0e97'
    context.resource.attributes = {}
    context.resource.address = address

    for attr, val in [("User", user),
                      ("Password", password),
                      ("Sessions Concurrency Limit", 1),
                      ("SNMP Read Community", "public"),
                      ("SNMP Version", "2"),
                      ("Enable SNMP", "True"),
                      ("Disable SNMP", "False"),
                      ("CLI Connection Type", "ssh")]:

        context.resource.attributes['{}.{}'.format(F5BigIPFirewallShell2GDriver.SHELL_NAME, attr)] = val

    context.connectivity = mock.MagicMock()
    context.connectivity.server_address = cs_address

    dr = F5BigIPFirewallShell2GDriver()
    dr.initialize(context)

    with mock.patch('__main__.get_api') as get_api:
        get_api.return_value = type('api', (object,), {
            'DecryptPassword': lambda self, pw: type('Password', (object,), {'Value': pw})()})()

        result = dr.get_inventory(context=context)

        for res in result.resources:
            print res.__dict__

