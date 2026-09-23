import click

from SigridSystemMetadata.SigridCustomer import SigridCustomer

@click.command()
@click.option('-c', '--customer', required=True, help='Customer name')
@click.option('-o', '--out_file', required=True, help='Excel file to write')
@click.option('-t', '--token', required=True, envvar='SIGRID_CI_TOKEN', help='Sigrid token (defaults to the SIGRID_CI_TOKEN environment variable)')
@click.option('-u', '--url', default=None, help='Base Sigrid URL (Default: https://sigrid-says.com)')
@click.option('-f', '--system_file', required=False, help='File with list of systems')
@click.option('-s', '--system', required=False, help='Sigrid system')
def export_security_results(customer, out_file, token, system_file, system, url):
    cust = SigridCustomer(customer=customer, token=token, base_url=url)
    cust.get_available_systems()

    systems = None

    if system_file is not None:
        with open(system_file, 'r') as file:
            systems = [s.strip() for s in file.readlines()]
    elif system is not None:
        systems=[system]

    cust.write_security_excel(out_file, systems)