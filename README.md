# Homebudget Django

The I don't know how manieth time I created this project. This time trying to match logic across all the projects

## Testing

Testing is done with pytest. The biggest reason for this is to support VsCode.
The default unittest framework of Python doesn't work with `python manage.py`.
See [the GitHub issue](https://github.com/microsoft/vscode-python/issues/73) for more info.
At the time of writing this issue is still open

### Pytest will not recreate the DB. Be aware when doing schema changes

In `pytest.ini` the setting `addopts = --reuse-db` is added.
This causes the test suite to not recreate the database if it already exists.
**When creating a new migration, run pytest once as follows**:

```bash
pytest --create-db
```

## Database

PostgreSQL is used as database provider.

### Windows WSL

Note that on my WSL 2, postgresql is turned off by default. Enable it by doing the following:

```bash
sudo service postgresql start
```