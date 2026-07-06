import json
import click

from SigridRest.SigridGetMetadataCommand import SigridGetMetadataCommand
from SigridSystemMetadata.SigridCustomer import SigridCustomer

@click.command()
@click.option('-c', '--customer', required=True, help='Customer name')
@click.option('-i', '--input_file', required=True, help='Input Excel file')
@click.option('-t', '--token', required=True, envvar='SIGRID_CI_TOKEN', help='Sigrid token (defaults to the SIGRID_CI_TOKEN environment variable)')
@click.option('-u', '--url', default=None, help='Base Sigrid URL (Default: https://sigrid-says.com)')
@click.option('-d', '--dry_run', is_flag=True, help="Don't do the patch, just print what would have been done.")
def import_portfolio_metadata(customer, input_file, token, dry_run, url):
    cust = SigridCustomer(customer=customer, token=token, base_url=url)
    cust.read_metadata_excel(input_file)

    current_portfolio_data = json.loads(SigridGetMetadataCommand(customer, token, base_url=url).do_request())

    for system in cust.systems.values():
        current = next((dat for dat in current_portfolio_data if dat["systemName"] == system.get_name()), None)
        if current is None:
            print(f"We wanted to patch {system.get_name()} but it doesn't exist in Sigrid")
            continue
        system.patch_metadata(dry_run=dry_run,
                              current=current)
