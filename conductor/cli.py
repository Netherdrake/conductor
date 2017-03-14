import click
from click import echo


@click.group()
def witness():
    pass


@witness.command()
def init():
    """ Add your witness account. """
    echo('hi')

    # see if wallet password is present
      # if not, create wallet
    # ask for witness name
      # if active key not present, set it
    # auto-import blockchain settings. ask user to confirm each one.
    # ask if we should enable the witness (if disabled)


