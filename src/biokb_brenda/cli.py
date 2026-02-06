import click
from sqlalchemy import create_engine

from biokb_brenda import __version__
from biokb_brenda.constants import NEO4J_USER, PROJECT_NAME
from biokb_brenda.db.manager import DbManager
from biokb_brenda.rdf.neo4j_importer import Neo4jImporter
from biokb_brenda.rdf.turtle import TurtleCreator
import logging

def setup_logging(ctx, param, value):
    # Only set up logging if the user actually asks for it
    if value == 1:
        logging.getLogger("biokb_ipni").setLevel(logging.INFO)
    elif value >= 2:
        logging.getLogger("biokb_ipni").setLevel(logging.DEBUG)

    # We must add a handler so the logs actually print to the screen
    if value > 0:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logging.getLogger("fetcher").addHandler(ch)

    return value


@click.group()
@click.version_option(__version__)
@click.option("-v", count=True, callback=setup_logging, expose_value=False)
def main():
    """Import in RDBMS, create turtle files and import into Neo4J.

    Please follow the steps:\n
    1. Import data using `import-data` command.\n
    2. Create TTL files using `create-ttls` command.\n
    3. Import TTL files into Neo4j using `import-neo4j` command.\n
    """
    pass


@main.command("import-data")
@click.option(
    "-f",
    "--force-download",
    is_flag=True,
    type=bool,
    default=False,
    help="Force re-download of the source file [default: False]",
)
@click.option(
    "-k",
    "--keep-files",
    is_flag=True,
    type=bool,
    default=False,
    help="Keep downloaded source files after import [default: False]",
)
@click.option(
    "-c",
    "--connection-string",
    type=str,
    default=f"sqlite:///{PROJECT_NAME}.db",
    help=f"SQLAlchemy engine URL [default: sqlite:///{PROJECT_NAME}.db]",
)
def import_data(force_download: bool, connection_string: str, keep_files: bool):
    """Import data."""
    engine = create_engine(connection_string)
    DbManager(engine=engine).import_data(
        force_download=force_download, keep_files=keep_files
    )
    click.echo(f"Data imported successfully to {connection_string}")


@main.command("create-ttls")
@click.option(
    "-c",
    "--connection-string",
    type=str,
    default=f"sqlite:///{PROJECT_NAME}.db",
    help=f"SQLAlchemy engine URL [default: sqlite:///{PROJECT_NAME}.db]",
)
def create_ttls(connection_string: str):
    """Create TTL files from local database."""
    path_to_zip = TurtleCreator(create_engine(connection_string)).create_ttls()
    click.echo(
        f"Path to the zip file containing all generated Turtle files. {path_to_zip}"
    )


@main.command("import-neo4j")
@click.option("--uri", "-i", default="bolt://localhost:7687", help="Neo4j database URI")
@click.option("--user", "-u", default=NEO4J_USER, help="Neo4j username")
@click.option("--password", "-p", required=True, help="Neo4j password")
def import_neo4j(uri: str, user: str, password: str):
    """Import TTL files into Neo4j database."""
    Neo4jImporter(neo4j_uri=uri, neo4j_user=user, neo4j_pwd=password).import_ttls()


if __name__ == "__main__":
    main()
