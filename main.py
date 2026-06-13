import os
import subprocess
import datetime
import getpass
import paramiko

base_path = os.getcwd()
list_servers = os.path.join(base_path, "servers.txt")
report_result_path = os.path.join(base_path, "result_connection.txt")
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
username_user = input(f"Input username: ")
password_user = getpass.getpass(f"Input password: ")

def read_list_servers():
    with open(list_servers, "r") as file:
        next(file)
        list_ips = []
        for line in file:
            list_ips.append(f"{line}".strip())
        return list_ips            

def test_connection(list_ips):
    result_test_connection = []
    for ip in list_ips:
        test_ping = subprocess.run(f'ping -n 1 {ip}', capture_output=True, text=True)
        result_test_connection.append((ip, test_ping.returncode))
    return result_test_connection

def report_result_conneciton(result_test_connection):
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
                    port = 22
                )
                stdin_hostname, stdout_hostname, stderr_hostname = ssh.exec_command('hostname')
                stdin_uptime, stdout_uptime, stderr_uptime = ssh.exec_command('uptime -p') 
                stdin_disk, stdout_disk, stderr_disk = ssh.exec_command("df -h / | awk 'NR==2 {print $5}'")
                stdin_memory, stdout_memory, stderr_memory = ssh.exec_command("free -m | awk 'NR==2 {print (($2-$7)/$7*100)\"%\"}'")
                stdin_1m, stdout_1m, stderr_1m = ssh.exec_command("cat /proc/loadavg | awk '{print $1}'")
                stdin_5m, stdout_5m, stderr_5m = ssh.exec_command("cat /proc/loadavg | awk '{print $2}'")
                stdin_15m, stdout_15m, stderr_15m = ssh.exec_command("cat /proc/loadavg | awk '{print $3}'")
                stdin_nproc, stdout_nproc, stdeer_nproc = ssh.exec_command("nproc")
                stdin_close, stdout_close, stderr_close = ssh.exec_command('exit')
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
            except:
                ssh_connection_result.append((
                    ip, "unknown", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "SSH Failed"
                ))
    return ssh_connection_result


def health_evaluation(ssh_connection_result):
    overal_status = []
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
                overal_status.append(f"Critical")
            elif "Warning" in status:
                overal_status.append("Warning")
            else:
                overal_status.append("Healthy")
        else:
            overal_status.append("Unreachable")
    print(overal_status)
        
            

list_ips = read_list_servers()
result_test_connection = test_connection(list_ips)
ssh_connection_result = ssh_connection(result_test_connection)

report_result_conneciton(result_test_connection)
health_evaluation(ssh_connection_result)
