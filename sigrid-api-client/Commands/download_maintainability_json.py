import json
from datetime import date as date_type

import click

from SigridSystemMetadata.SigridCustomer import SigridCustomer


def validate_date_format(ctx, param, value):
    if value is not None:
        try:
            value = date_type.fromisoformat(value).isoformat()
        except ValueError:
            raise click.BadParameter(f"'{value}' is not a valid localdate or accepted ISO format, expected format is YYYY-MM-DD, e.g. '2026-01-01'")
    return value


@click.command()
@click.option('-c', '--customer', required=True, help='Customer name')
@click.option('-o', '--out_file', required=True, help='JSON to write')
@click.option('-t', '--token', required=True, envvar='SIGRID_CI_TOKEN', help='Sigrid token (defaults to the SIGRID_CI_TOKEN environment variable)')
@click.option('-u', '--url', default=None, help='Base Sigrid URL (Default: https://sigrid-says.com)')
@click.option('-s', '--system', required=True, help='Sigrid system')
@click.option('-d', '--date', required=False, callback=validate_date_format, help="Snapshot date, in localdate format (e.g. '2026-01-01')")
def download_maintainability_json(customer, out_file, token, system, date, url):
    cust = SigridCustomer(customer=customer, token=token, base_url=url)
    data = cust.get_JSON_for_system(system, date)

    with open(out_file, 'w') as file:
        json.dump(data, file, indent=2)