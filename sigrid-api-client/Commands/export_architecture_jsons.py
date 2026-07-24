import os

import click

from SigridSystemMetadata.SigridCustomer import SigridCustomer

@click.command()
@click.option('-c', '--customer', required=True, help='Customer name')
@click.option('-o', '--out_directory', required=False, help='Directory to write portfolio JSONs to')
@click.option('-t', '--token', required=True, envvar='SIGRID_CI_TOKEN', help='Sigrid token (defaults to the SIGRID_CI_TOKEN environment variable)')
@click.option('-u', '--url', default=None, help='Base Sigrid URL (Default: https://sigrid-says.com)')
@click.option('-s', '--system', required=False, help='Optional Sigrid system to export')
@click.option('-f', '--out_file', required=False, help='File to write single-system JSON to')
def export_architecture_jsons(customer, out_directory, token, system, out_file, url):
    cust = SigridCustomer(customer=customer, token=token, base_url=url)
    if system is not None:
        if out_file is None:
            raise click.UsageError("--out_file must be defined to retrieve a single system's JSON")
        cust.write_architecture_JSON(system, out_file)
    else:
        if out_directory is None:
            raise click.UsageError('--out_directory must be defined to retrieve all JSONs for a portfolio')
        if not os.path.exists(out_directory):
            os.makedirs(out_directory)
        cust.write_all_architecture_JSONs(out_directory)

