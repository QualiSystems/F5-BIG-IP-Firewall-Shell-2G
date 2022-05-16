# # old imports ---
# from cloudshell.core.context.error_handling_context import ErrorHandlingContext
# from cloudshell.devices.driver_helper import (
#     get_api,
#     get_cli,
#     get_logger_with_thread_id,
#     parse_custom_commands,
# )
# from cloudshell.devices.runners.run_command_runner import RunCommandRunner
# from cloudshell.devices.runners.state_runner import StateRunner
# from cloudshell.devices.standards.firewall.configuration_attributes_structure import (
#     create_firewall_resource_from_context,
# )
# from cloudshell.f5.cli.f5_cli_handler import F5CliHandler
# from cloudshell.f5.runners.f5_configuration_runner import F5ConfigurationRunner
# from cloudshell.f5.runners.f5_firmware_runner import F5FirmwareRunner
# from cloudshell.f5.snmp.f5_snmp_handler import F5SnmpHandler
# from cloudshell.firewall.firewall_resource_driver_interface import (
#     FirewallResourceDriverInterface,
# )
# from cloudshell.shell.core.driver_utils import GlobalLock
# from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
#
# from f5.firewall.runners.f5_autoload_runner import F5FirewallAutoloadRunner

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.standards.firewall.driver_interface import (
    FirewallResourceDriverInterface,
)
from cloudshell.shell.standards.firewall.resource_config import FirewallResourceConfig
from cloudshell.shell.core.driver_utils import GlobalLock
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.service.session_pool_manager import SessionPoolManager
from cloudshell.f5.cli.f5_cli_configurator import F5CliConfigurator
from cloudshell.f5.flows.f5_enable_disable_snmp_flow import (
    F5EnableDisableSnmpFlow,
)
from cloudshell.snmp.snmp_configurator import EnableDisableSnmpConfigurator
from cloudshell.shell.standards.firewall.autoload_model import FirewallResourceModel
from cloudshell.f5.flows.f5_autoload_flow import BigIPAutoloadFlow
from cloudshell.shell.flows.command.basic_flow import RunCommandFlow
from cloudshell.f5.flows.f5_configuration_flow import F5ConfigurationFlow
from cloudshell.f5.flows.f5_firmware_flow import F5FirmwareFlow
from cloudshell.f5.flows.f5_state_flow import F5StateFlow
from cloudshell.shell.core.orchestration_save_restore import OrchestrationSaveRestore


class F5BigIPFirewallShell2GDriver(ResourceDriverInterface, FirewallResourceDriverInterface):
    SUPPORTED_OS = ["BIG[ -]?IP"]
    SHELL_NAME = "F5 BIG IP Firewall 2G"

    def __init__(self):
        # super(F5BigIPFirewallShell2GDriver, self).__init__() # todo ?
        self._cli = None

    def initialize(self, context):
        """Initialize the driver session.

        :param InitCommandContext context: the context the command runs on
        :rtype: str
        """
        resource_config = FirewallResourceConfig.from_context(self.SHELL_NAME, context)
        session_pool_size = int(resource_config.sessions_concurrency_limit)
        self._cli = CLI(
            SessionPoolManager(max_pool_size=session_pool_size, pool_timeout=100)
        )
        return "Finished initializing"

    @GlobalLock.lock
    def get_inventory(self, context):
        """Return device structure with all standard attributes.

        :param ResourceCommandContext context: ResourceCommandContext object with all
          Resource Attributes inside
        :return: response
        :rtype: str
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME, context, api, self.SUPPORTED_OS
            )

            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )
            enable_disable_snmp_flow = F5EnableDisableSnmpFlow(cli_configurator, logger)
            snmp_configurator = EnableDisableSnmpConfigurator(
                enable_disable_snmp_flow, resource_config, logger
            )

            resource_model = FirewallResourceModel.from_resource_config(resource_config)

            autoload_operations = BigIPAutoloadFlow(snmp_configurator, logger)
            logger.info("Autoload started")
            response = autoload_operations.discover(self.SUPPORTED_OS, resource_model)
            logger.info("Autoload completed")
            return response

    def run_custom_command(self, context, custom_command):
        """Executes a custom command on the device.

        :param ResourceCommandContext context: The context object
         for the command with resource and reservation info
        :param str custom_command: The command to run
        :return: the command result text
        :rtype: str
        """
        with LoggingSessionContext(context) as logger:
            # logger.info("Run custom command started")
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            send_command_operations = RunCommandFlow(logger, cli_configurator)
            response = send_command_operations.run_custom_command(custom_command)
            # logger.info("Run custom command ended with response: {}".format(response))
            return response

    def run_custom_config_command(self, context, custom_command):
        """Executes a custom command on the device in configuration mode.

        :param ResourceCommandContext context: The context object
         for the command with resource and reservation info
        :param str custom_command: The command to run
        :return: the command result text
        :rtype: str
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            send_command_operations = RunCommandFlow(logger, cli_configurator)
            result_str = send_command_operations.run_custom_config_command(
                custom_command
            )
            return result_str

    def save(self, context, folder_path, configuration_type, vrf_management_name):
        """Save a configuration file to the provided destination.

        :param ResourceCommandContext context: The context object
         for the command with resource and reservation info
        :param str folder_path: The path to the folder in which the configuration
         file will be saved
        :param str configuration_type: startup or running config
        :return The configuration file name
        :rtype: str
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            if not configuration_type:
                configuration_type = "running"

            if not vrf_management_name:
                vrf_management_name = resource_config.vrf_management_name

            configuration_operations = F5ConfigurationFlow(
                resource_config, logger, cli_configurator
            )
            logger.info("Save started")
            response = configuration_operations.save(
                folder_path=folder_path,
                configuration_type=configuration_type,
                vrf_management_name=vrf_management_name,
            )
            logger.info("Save completed")
            return response

    @GlobalLock.lock  # todo needed?
    def restore(self, context, path, configuration_type, restore_method, vrf_management_name):
        """Restores a configuration file.

        :param ResourceCommandContext context: The context object for the command
         with resource and reservation info
        :param str path: The path to the configuration file, including the
         configuration file name
        :param str restore_method: Determines whether the restore should append or
         override the current configuration
        :param str configuration_type: Specify whether the file should update
         the startup or running config
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            if not configuration_type:
                configuration_type = "running"

            if not restore_method:
                restore_method = "override"

            if not vrf_management_name:
                vrf_management_name = resource_config.vrf_management_name

            configuration_operations = F5ConfigurationFlow(
                resource_config, logger, cli_configurator
            )
            logger.info("Restore started")
            configuration_operations.restore(
                path=path,
                restore_method=restore_method,
                configuration_type=configuration_type,
                vrf_management_name=vrf_management_name,
            )
            logger.info("Restore completed")


    @GlobalLock.lock
    def load_firmware(self, context, path, vrf_management_name):
        """Upload and updates firmware on the resource.

        :param ResourceCommandContext context: The context object
         for the command with resource and reservation info
        :param str path: path to tftp server where firmware file is stored
        """

        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            if not vrf_management_name:
                vrf_management_name = resource_config.vrf_management_name

            logger.info("Start Load Firmware")
            firmware_operations = F5FirmwareFlow(logger, cli_configurator)
            response = firmware_operations.load_firmware(
                path=path, vrf_management_name=vrf_management_name
            )
            logger.info("Finish Load Firmware: {}".format(response))

        # logger = get_logger_with_thread_id(context)
        # logger.info("Load firmware command started")
        #
        # with ErrorHandlingContext(logger):
        #     resource_config = create_firewall_resource_from_context(
        #         self.SHELL_NAME, self.SUPPORTED_OS, context
        #     )
        #     cs_api = get_api(context)
        #
        #     cli_handler = F5CliHandler(self._cli, resource_config, logger, cs_api)
        #
        #     logger.info("Start Loading Firmware...")
        #     firmware_operations = F5FirmwareRunner(
        #         cli_handler=cli_handler, logger=logger
        #     )
        #
        #     response = firmware_operations.load_firmware(path=path)
        #     logger.info(
        #         "Load firmware command completed with response: {}".format(response)
        #     )
        #
        #     return response

    def shutdown(self, context):
        """Sends a graceful shutdown to the device.

        :param ResourceCommandContext context: The context object
         for the command with resource and reservation info
        """

        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            state_operations = F5StateFlow(
                logger, resource_config, cli_configurator, api
            )
            return state_operations.shutdown()

    def orchestration_save(self, context, mode, custom_params):
        """Saves the Shell state and returns a description of the saved artifacts.

        This command is intended for API use only by sandbox orchestration
        scripts to implement a save and restore workflow
        :param ResourceCommandContext context: the context object containing
         resource and reservation info
        :param str mode: Snapshot save mode, can be one of two values
         'shallow' (default) or 'deep'
        :param str custom_params: Set of custom parameters for the save operation
        :return: SavedResults serialized as JSON
        :rtype: OrchestrationSaveResult
        """

        if not mode:
            mode = "shallow"

        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            configuration_operations = F5ConfigurationFlow(
                resource_config, logger, cli_configurator
            )

            logger.info("Orchestration save started")

            response = configuration_operations.orchestration_save(
                mode=mode, custom_params=custom_params
            )
            response_json = OrchestrationSaveRestore(
                logger, resource_config.name
            ).prepare_orchestration_save_result(response)
            logger.info("Orchestration save completed")
            return response_json

    def orchestration_restore(self, context, saved_artifact_info, custom_params):
        """Restores a saved artifact previously saved by this Shell.

        :param ResourceCommandContext context: The context object
         for the command with resource and reservation info
        :param str saved_artifact_info: A JSON string representing the state
         to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        """

        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            configuration_operations = F5ConfigurationFlow(
                resource_config, logger, cli_configurator
            )

            logger.info("Orchestration restore started")
            configuration_operations.orchestration_restore(
                saved_artifact_info=saved_artifact_info, custom_params=custom_params
            )
            logger.info("Orchestration restore completed")

            logger.info("Orchestration restore started")
            restore_params = OrchestrationSaveRestore(
                logger, resource_config.name
            ).parse_orchestration_save_result(saved_artifact_info, custom_params)
            configuration_operations.restore(**restore_params)
            logger.info("Orchestration restore completed")

        #
        # logger = get_logger_with_thread_id(context)
        # logger.info("Orchestration restore command started")
        #
        # with ErrorHandlingContext(logger):
        #     resource_config = create_firewall_resource_from_context(
        #         self.SHELL_NAME, self.SUPPORTED_OS, context
        #     )
        #     cs_api = get_api(context)
        #
        #     cli_handler = F5CliHandler(self._cli, resource_config, logger, cs_api)
        #
        #     configuration_operations = F5ConfigurationRunner(
        #         cli_handler=cli_handler,
        #         logger=logger,
        #         resource_config=resource_config,
        #         api=cs_api,
        #     )
        #
        #     configuration_operations.orchestration_restore(
        #         saved_artifact_info=saved_artifact_info, custom_params=custom_params
        #     )
        #
        #     logger.info("Orchestration restore command completed")

    def health_check(self, context):
        """Checks if the device is up and connectable.

        :param ResourceCommandContext context: ResourceCommandContext object
         with all Resource Attributes inside
        :return: Success or fail message
        :rtype: str
        """
        with LoggingSessionContext(context) as logger:
            api = CloudShellSessionContext(context).get_api()

            resource_config = FirewallResourceConfig.from_context(
                self.SHELL_NAME,
                context,
                api,
                self.SUPPORTED_OS,
            )
            cli_configurator = F5CliConfigurator(
                self._cli, resource_config, logger
            )

            state_operations = F5StateFlow(
                logger, resource_config, cli_configurator, api
            )
            return state_operations.health_check()

    def cleanup(self):
        """Destroy the driver session.

        This function is called everytime a driver instance is destroyed.
        This is a good place to close any open sessions, finish writing to log files
        """
        pass


if __name__ == "__main__":
    # todo clean this all up
    import mock
    from cloudshell.shell.core.driver_context import (
        ReservationContextDetails,
        ResourceCommandContext,
        ResourceContextDetails,
    )

    address = "192.168.26.52"
    user = "admin"
    password = "admin"
    cs_address = "192.168.85.36"
    enable_password = 'idkdude'
    ro_community = 'quali'

    auth_key = "h8WRxvHoWkmH8rLQz+Z/pg=="
    api_port = 8029

    from mock import create_autospec
    SHELL_NAME = F5BigIPFirewallShell2GDriver.SHELL_NAME + '.'

    context = create_autospec(ResourceCommandContext)
    context.resource = create_autospec(ResourceContextDetails)
    context.resource.name = address
    context.resource.fullname = 'test biggieip'
    context.resource.family = 'CS_Firewall'
    context.reservation = create_autospec(ReservationContextDetails)
    context.reservation.reservation_id = 'test_id'
    context.reservation.domain = 'Global'
    context.resource.attributes = {}
    context.resource.id = ""
    context.resource.attributes['{}User'.format(SHELL_NAME)] = user
    context.resource.attributes['{}Password'.format(SHELL_NAME)] = password
    context.resource.attributes['{}host'.format(SHELL_NAME)] = address
    # context.resource.attributes['{}Enable Password'.format(SHELL_NAME)] = enable_password
    # context.resource.attributes[
    #     '{}Backup Location'.format(SHELL_NAME)] = '192.168.105.3/192.168.105.55-running-290620-100535'
    # context.resource.attributes['{}Backup Type'.format(SHELL_NAME)] = 'ftp'
    # context.resource.attributes['{}Backup User'.format(SHELL_NAME)] = 'test_user'
    # context.resource.attributes['{}Backup Password'.format(SHELL_NAME)] = 'test_password'
    # context.resource.attributes['{}Backup User'.format(SHELL_NAME)] = 'gns3'
    # context.resource.attributes['{}Backup Password'.format(SHELL_NAME)] = 'gns3'
    context.resource.address = address

    context.connectivity = mock.MagicMock()
    context.connectivity.admin_auth_token = 'xf5flrrr2o4tfisvd5iy13td'
    # context.connectivity.admin_auth_token = 'Er4rWgbKv06-j3ZhUp9mEw2'
    context.connectivity.server_address = '192.168.85.36'

    context.resource.attributes['{}SNMP Version'.format(SHELL_NAME)] = 'v3'
    # context.resource.attributes['{}SNMP Version'.format(SHELL_NAME)] = '3'
    context.resource.attributes['{}SNMP Read Community'.format(SHELL_NAME)] = ro_community
    context.resource.attributes['{}SNMP V3 User'.format(SHELL_NAME)] = 'v3admin2'
    context.resource.attributes['{}SNMP V3 Password'.format(SHELL_NAME)] = 'v3adminauth'
    context.resource.attributes['{}SNMP V3 Private Key'.format(SHELL_NAME)] = 'v3adminpriv'
    context.resource.attributes['{}SNMP V3 Authentication Protocol'.format(SHELL_NAME)] = 'MD5'
    context.resource.attributes['{}SNMP V3 Privacy Protocol'.format(SHELL_NAME)] = 'DES'
    context.resource.attributes['{}CLI Connection Type'.format(SHELL_NAME)] = 'auto'

    # configure snmpv3 add access snmpgroup sec-level priv read-view randomvvv write-view randomvvv
    # configure snmpv3 add user snmpuser authentication md5 snmppassword privacy aes privkey111

    context.resource.attributes['{}Enable SNMP'.format(SHELL_NAME)] = 'True'
    context.resource.attributes['{}Disable SNMP'.format(SHELL_NAME)] = 'False'
    context.resource.attributes['{}Sessions Concurrency Limit'.format(SHELL_NAME)] = 1

    # context.resource.attributes['{}Console Server IP Address'.format(SHELL_NAME)] = '192.168.26.111'
    context.resource.attributes['{}Console User'.format(SHELL_NAME)] = ''
    context.resource.attributes['{}Console Password'.format(SHELL_NAME)] = ''
    context.resource.attributes['{}Console Port'.format(SHELL_NAME)] = 17016

    context.connectivity = mock.MagicMock()
    context.connectivity.server_address = cs_address

    dr = F5BigIPFirewallShell2GDriver()
    dr.initialize(context)

    from mock import patch
    with patch('driver.CloudShellSessionContext') as get_api:
        api = type('api', (object,),
                   {'DecryptPassword': lambda self, pw: type('Password', (object,), {'Value': pw})()})()
        # get_api.return_value = api

        get_api.return_value.get_api.return_value = api
        # driver.SUPPORTED_OS = "."

        response_autoload = dr.get_inventory(context)
        print('{}'.format(response_autoload))
