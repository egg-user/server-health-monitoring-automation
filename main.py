"""
Server Health Monitoring Automation

Collects server metrics through SSH and generates
health reports based on disk usage, memory usage,
and CPU load.

"""

import os
import subprocess
import datetime
import getpass
import paramiko


base_path = os.getcwd()
list_servers = os.path.join(base_path, "servers.txt")
report_result_path = os.path.join(base_path, "result_connection.txt")
current_date = datetime.datetime.now().strftime("%Y%m%d")
generate_report_path = os.path.join(base_path, "output", f"server_health_{current_date}.txt")
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
username_user = input(f"Input username: ")
password_user = getpass.getpass(f"Input password: ")

os.makedirs(
    os.path.join(base_path, "output"),
    exist_ok=True
)

def read_list_servers():
    """
    Read server IP addresses from servers.txt.

    Returns:
        list: List of server IP addresses.
    """

    with open(list_servers, "r") as file:
        next(file)
        list_ips = []
        for line in file:
            list_ips.append(f"{line}".strip())
        return list_ips            

def test_connection(list_ips):
    """
    Test network connectivity to each server using ping.

    Args:
        list_ips (list): List of server IP addresses.

    Returns:
        list: List of tuples containing IP address and ping result code.
    """

    result_test_connection = []
    for ip in list_ips:
        test_ping = subprocess.run(f'ping -n 1 {ip}', capture_output=True, text=True)
        result_test_connection.append((ip, test_ping.returncode))
    return result_test_connection

def report_result_connection(result_test_connection):
    """
    Generate a connectivity report showing UP and DOWN servers.

    Args:
        result_test_connection (list): Ping test results.

    Returns:
        None
    """

    with open(report_result_path, "w") as file:
        file.write(f"=== server status report ===\n\n".upper())
        file.write(f"Generated : {current_time}\n\n")
        up_count = 0
        down_count = 0
        total_server_count = 0
        for ip, result in result_test_connection:
            if result == 0:
                file.write(f"{ip} : UP\n")
                up_count += 1
                total_server_count += 1
            else:
                file.write(f"{ip} : DOWN\n")
                down_count += 1
                total_server_count += 1
        file.write(f"\nTotal servers : {total_server_count}\n")
        file.write(f"UP : {up_count}\n")
        file.write(f"DOWN : {down_count}\n")

def ssh_connection(result_test_connection):
    """
    Connect to reachable servers via SSH and collect system metrics.

    Collected metrics:
        - Hostname
        - Uptime
        - Disk usage
        - Memory usage
        - Load average (1m, 5m, 15m)
        - CPU core count

    Args:
        result_test_connection (list): Ping test results.

    Returns:
        list: Server monitoring data collected from SSH sessions.
    """

    ssh_connection_result = []
    for ip, result in result_test_connection:
        if result == 0:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname = ip,
                    username = username_user,
                    password = password_user,
                    port = 22,
                    timeout=5
                )
                stdin_hostname, stdout_hostname, stderr_hostname = ssh.exec_command('hostname')
                stdin_uptime, stdout_uptime, stderr_uptime = ssh.exec_command('uptime -p') 
                stdin_disk, stdout_disk, stderr_disk = ssh.exec_command("df -h / | awk 'NR==2 {print $5}'")
                stdin_memory, stdout_memory, stderr_memory = ssh.exec_command("free -m | awk 'NR==2 {print (($2-$7)/$7*100)\"%\"}'")
                stdin_1m, stdout_1m, stderr_1m = ssh.exec_command("cat /proc/loadavg | awk '{print $1}'")
                stdin_5m, stdout_5m, stderr_5m = ssh.exec_command("cat /proc/loadavg | awk '{print $2}'")
                stdin_15m, stdout_15m, stderr_15m = ssh.exec_command("cat /proc/loadavg | awk '{print $3}'")
                stdin_nproc, stdout_nproc, stderr_nproc = ssh.exec_command("nproc")
                hostname = stdout_hostname.read().decode().strip()
                uptime = stdout_uptime.read().decode().strip()
                disk = stdout_disk.read().decode().strip()
                memory = stdout_memory.read().decode().strip()
                load_1m = stdout_1m.read().decode().strip()
                load_5m = stdout_5m.read().decode().strip()
                load_15m = stdout_15m.read().decode().strip()
                nproc = stdout_nproc.read().decode().strip()
                ssh_connection_result.append((
                    ip, hostname, uptime, disk, memory, load_1m, load_5m, load_15m, nproc))
                ssh.close()
            except Exception as e:
                ssh_connection_result.append((
                    ip, "unknown", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "SSH Failed"
                ))
                print(f"{ip}: {e}")
    return ssh_connection_result


def health_evaluation(ssh_connection_result):
    """
    Evaluate server health based on disk, memory, and CPU load ratio.

    Health status:
        - Healthy
        - Warning
        - Critical
        - Unreachable

    Args:
        ssh_connection_result (list): Raw monitoring data from SSH.

    Returns:
        list: Monitoring data with overall health status.
    """

    overall_status = []
    for ip, hostname, uptime, disk, memory, load_1m, load_5m, load_15m, nproc in ssh_connection_result:
        if nproc != "SSH Failed":
            status = []
            disk_number = int(disk.replace("%", ""))
            memory_number = float(memory.replace("%", ""))
            load_1m_number = float(load_1m)
            nproc_number = int(nproc)
            load_ratio = load_1m_number/nproc_number
            if disk_number > 90:
                status.append("Critical")
            elif disk_number > 80:
                status.append("Warning")
            else:
                status.append("Healthy")
            if memory_number > 90:
                status.append("Critical")
            elif memory_number > 80:
                status.append("Warning")
            else:
                status.append("Healthy")
            if load_ratio >= 1 :
                status.append("Critical")
            elif load_ratio > 0.7:
                status.append("Warning")
            else:
                status.append("Healthy")
            if "Critical" in status:
                overall = "Critical"
            elif "Warning" in status:
                overall = "Warning"
            else:
                overall = "Healthy"
        else:
            overall = "Unreachable"
        overall_status.append((
            ip, hostname, uptime, disk, memory, load_1m, load_5m, load_15m, overall
        ))
    return overall_status

def generate_report(overall_status):
    """
    Generate a server health monitoring report in text format.

    Report includes:
        - Server information
        - Resource utilization
        - Overall health status
        - Summary statistics

    Args:
        overall_status (list): Evaluated server health results.

    Returns:
        None
    """

    with open(generate_report_path, "w") as file:
        file.write("==================================================\n")
        file.write("server health monitoring report\n".upper())
        file.write("==================================================\n\n")
        server_count = 0
        healthy_count = 0
        warning_count = 0
        critical_count = 0
        unreachable_count = 0
        file.write(f"Generated: {current_time}\n\n")
        for ip, hostname, uptime, disk, memory, load_1m, load_5m, load_15m, overall in overall_status:
            if overall != "Unreachable":
                file.write(
                    "--------------------------------------------------\n"
                    f"IP Address     : {ip}\n"
                    f"Hostname       : {hostname}\n"
                    f"Status         : {overall}\n\n"
                    f"Uptime         : {uptime}\n"
                    f"Disk Usage     : {disk}\n"
                    f"Memory         : {memory}\n"
                    f"Load 1m        : {load_1m}\n"
                    f"Load 5m        : {load_5m}\n"
                    f"Load 15m       : {load_15m}\n\n"
                )
                server_count += 1
                if overall == "Healthy":
                    healthy_count += 1
                elif overall == "Warning":
                    warning_count += 1
                else:
                    critical_count += 1
            else:
                file.write(
                    "--------------------------------------------------\n"
                    f"IP Address     : {ip}\n"
                    f"Hostname       : {hostname}\n"
                    f"Status         : {overall}\n\n"
                    "SSH Connection Failed\n\n"
                )
                server_count += 1
                unreachable_count += 1
        file.write(
            "==================================================\n"
            "Summary\n"
            "==================================================\n\n"
        )
        file.write(
            f"Total Servers  : {server_count}\n"
            f"Healthy        : {healthy_count}\n"
            f"Warning        : {warning_count}\n"
            f"Critical       : {critical_count}\n"
            f"Unreachable    : {unreachable_count}\n"
        )

        
            

if __name__ == "__main__":
    list_ips = read_list_servers()
    result_test_connection = test_connection(list_ips)
    ssh_connection_result = ssh_connection(result_test_connection)
    overall_status = health_evaluation(ssh_connection_result)
    generate_report(overall_status)
    report_result_connection(result_test_connection)
