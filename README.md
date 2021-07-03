# Ludus

(Temporary name.)

## Components

### Auto-chess

[auto_chess/] defines a simple auto-chess game, where two players select teams of
monsters, which then battle each other automatically until one player's monsters are all
dead.

Instructions for defining new cards by subclassing `Card` are in [auto_chess/__init__.py].

### Analysis

[analysis/] defines a generic framework for computing or approximating the Pareto frontier
of a deckbuilding game. It includes machinery for using
[Pathos](https://pypi.org/project/pathos/) for multiprocessing to parallelize computation.

## Running it

### Setup

Install pipenv
```
pip install pipenv
```

Install from `Pipfile`
```
pipenv install
```

Activate virtual environment
```
pipenv shell
```

### Dev

Add a dependency to `Pipfile`
```
pipenv install <package>
```

### Testing

Phoebe wrote a beautiful test script which will run `mypy` (the static type checker),
`pytest` (the unit tester), and `flake8` (the style checker). Run with:

```
pipenv run test
```
