# Server Health Monitoring Automation

## Overview

Server Health Monitoring Automation is a Python-based monitoring tool that connects to Linux servers via SSH, collects system health metrics, evaluates server status, and generates detailed health reports.

This project was created to automate routine server monitoring tasks commonly performed by System Administrators, Infrastructure Engineers, and Network Engineers.

The script performs connectivity checks, gathers server health information, evaluates resource utilization against predefined thresholds, and generates a structured monitoring report.

---

## Features

* ICMP connectivity check (Ping)
* SSH connectivity validation
* Hostname collection
* Uptime monitoring
* Disk usage monitoring
* Memory usage monitoring
* Load average monitoring (1m, 5m, 15m)
* CPU load ratio calculation
* Health status evaluation
* Unreachable server detection
* Automated text report generation

---

## Technologies Used

* Python 3
* Paramiko
* Linux
* SSH
* Bash Commands
* Network Monitoring

---

## Requirements

* Python 3.10+
* Paramiko

Install dependencies:

```bash
pip install paramiko
```

---

## Usage

### 1. Prepare server list

Create a file named `servers.txt`.

Example:

```text
IP Address
192.168.1.138
192.168.1.178
```

### 2. Run the script

```bash
python main.py
```

### 3. Enter SSH credentials

```text
Input username: egg
Input password:
```

### 4. Generated files

The script generates:

```text
result_connection.txt
output/server_health_YYYYMMDD.txt
```

---

## Project Structure

```text
server-health-monitoring-automation/
│
├── main.py
├── servers.txt
├── result_connection.txt
├── output/
│   └── server_health_YYYYMMDD.txt
├── README.md
└── .gitignore
```

---

## Health Evaluation Logic

### Disk Usage

| Usage  | Status   |
| ------ | -------- |
| <= 80% | Healthy  |
| > 80%  | Warning  |
| > 90%  | Critical |

### Memory Usage

| Usage  | Status   |
| ------ | -------- |
| <= 80% | Healthy  |
| > 80%  | Warning  |
| > 90%  | Critical |

### CPU Load Ratio

Formula:

```text
Load Ratio = Load Average (1 Minute) / CPU Cores
```

| Ratio  | Status   |
| ------ | -------- |
| <= 0.7 | Healthy  |
| > 0.7  | Warning  |
| >= 1.0 | Critical |

The overall server status is determined by the highest severity level detected.

---

## Example Output

```text
==================================================
SERVER HEALTH MONITORING REPORT
==================================================

Generated: 2026-06-14 19:24:07

--------------------------------------------------
IP Address     : 192.168.1.138
Hostname       : eggvm0
Status         : Healthy

Uptime         : up 18 hours, 54 minutes
Disk Usage     : 15%
Memory         : 25.03%
Load 1m        : 0.00
Load 5m        : 0.00
Load 15m       : 0.00

--------------------------------------------------
IP Address     : 192.168.1.178
Hostname       : eggvm1
Status         : Healthy

Uptime         : up 9 hours, 7 minutes
Disk Usage     : 15%
Memory         : 23.07%
Load 1m        : 0.00
Load 5m        : 0.00
Load 15m       : 0.00

==================================================
Summary
==================================================

Total Servers  : 2
Healthy        : 2
Warning        : 0
Critical       : 0
Unreachable    : 0
```

---

## Learning Outcomes

Through this project, I practiced:

* Python automation
* SSH automation using Paramiko
* Linux system administration commands
* Infrastructure monitoring concepts
* Resource utilization analysis
* Report generation
* Error handling and exception management

---

## Future Improvements

* Export reports to CSV
* Export reports to Excel
* Email alert notifications
* Scheduled execution using Cron
* CPU utilization monitoring
* Web dashboard integration
* Multi-threaded server monitoring

