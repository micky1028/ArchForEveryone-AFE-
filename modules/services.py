from modules.core import run_command

def enable_service(service_name):
    run_command(["systemctl", "enable", "--now", service_name], as_root=True)