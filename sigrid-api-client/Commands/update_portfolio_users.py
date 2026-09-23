import click

from SigridSystemMetadata.SigridCustomer import SigridCustomer


@click.command()
@click.option('-c', '--customer', required=True, help='Customer name')
@click.option('-i', '--input_file', required=True, help='Input Excel file')
@click.option('-t', '--token', required=True, envvar='SIGRID_CI_TOKEN', help='Sigrid token (defaults to the SIGRID_CI_TOKEN environment variable)')
@click.option('-u', '--url', default=None, help='Base Sigrid URL (Default: https://sigrid-says.com)')
@click.option('-d', '--dry_run', help="Don't do the patch, just print what would have been done.", is_flag=True)
def update_portfolio_users(customer, input_file, token, dry_run, url):
    cust = SigridCustomer(customer=customer, token=token, base_url=url)
    cust.update_sigrid_users_from_excel(input_file, dry_run=dry_run)