import click

from Utils.ExcelUtils import create_template_from_array

HEADER = ["systemName", "externalID", "userName", "mendixToken", "teamServerBranch"]


@click.command()
@click.option('-o', '--output_file', help='Output excel sheet', required=True)
def generate_mendix_onboarding_template(output_file):
	"""Generate an Excel template to be filled in. Note: certain fields such as the mendixToken (PAT) may be provided globally through script flags."""
	create_template_from_array(HEADER, output_file)