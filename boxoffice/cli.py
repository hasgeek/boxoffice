from . import app


@app.cli.command('dbconfig')
def dbconfig():
    """Show required database configuration."""
    print(  # NOQA: T001
        '''
-- Pipe this into psql as a super user. Example:
-- flask dbconfig | sudo -u postgres psql boxoffice

CREATE EXTENSION IF NOT EXISTS pg_trgm;
'''
    )
