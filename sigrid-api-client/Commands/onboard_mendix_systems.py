import click

from SigridSystemMetadata.SigridCustomer import SigridCustomer




@click.command()
@click.option('-c', '--customer', required=True, help='Customer name')
@click.option('-i', '--input_file', required=True, help='Input Excel file')
@click.option('-t', '--token', required=True, envvar='SIGRID_CI_TOKEN', help='Sigrid token (defaults to the SIGRID_CI_TOKEN environment variable)')
@click.option('-u', '--url', default=None, help='Base Sigrid URL (Default: https://sigrid-says.com)')
@click.option('-p', '--pat', help="Valid Mendix PAT for systems if not included in the Excel file", required=False)
@click.option('-e', '--email', help="Email to associate with systems if not included in the Excel file", required=False)
@click.option('-d', '--dry_run', help="Don't do the patch, just print what would have been done.", is_flag=True)
@click.option('-o', '--output_file', help='Optional output Excel sheet containing returned data (e.g., Sigrid system name)', required=False)
def onboard_mendix_systems(customer, input_file, token, pat, email, dry_run, output_file, url):
    cust = SigridCustomer(customer=customer, token=token, base_url=url)
    cust.onboard_mendix_from_excel(input_file, pat=pat, username=email, dry_run=dry_run, output_file=output_file)