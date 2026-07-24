import click
import sys
import Commands.commands

@click.group()
def cli():
    pass

for cli_command in Commands.commands.clis:
    cli.add_command(cli_command)

def run():
    if len(sys.argv) == 2:
        command_name = sys.argv[1]
        if command_name in cli.commands:
            sys.argv.append('--help')
    cli()


if __name__ == "__main__":
    run()
