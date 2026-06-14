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
            f"Unreachable    : {uncreachable_count}\n"
        )