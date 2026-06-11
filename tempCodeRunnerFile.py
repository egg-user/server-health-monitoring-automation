            if memory_number > 90:
                status.append("Critical")
            elif memory_number > 80:
                status.append("Warning")
            else:
                status.append("Heatlhy")
            print(status)