import colorama
colorama.init()

def print_site_log(site_name, log, err=False):
    print(colorama.Fore.BLUE + colorama.Style.BRIGHT, end='')
    print(f'[{site_name}] ', end='')
    if err:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + 'Error: ', end='')
    print(colorama.Style.RESET_ALL, end='')
    print(log)