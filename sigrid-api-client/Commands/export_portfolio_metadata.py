import click

from SigridSystemMetadata.SigridCustomer import SigridCustomer


@click.command()
@click.option('-c', '--customer', required=True, help='Customer name')
@click.option('-o', '--out_file', required=True, help='Excel file to write to')
@click.option('-t', '--token', required=True, envvar='SIGRID_CI_TOKEN', help='Sigrid token (defaults to the SIGRID_CI_TOKEN environment variable)')
@click.option('-u', '--url', default=None, help='Base Sigrid URL (Default: https://sigrid-says.com)')
def export_portfolio_metadata(customer, out_file, token, url):
    cust = SigridCustomer(customer=customer, token=token, base_url=url)
    cust.get_available_systems_with_metadata()
    cust.write_metadata_excel(out_file)
