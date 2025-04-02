"""Console script for phone_app."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("phone")
    click.echo("=" * len("phone"))
    click.echo("Skeleton project created by Cookiecutter PyPackage")


if __name__ == "__main__":
    main()  # pragma: no cover
