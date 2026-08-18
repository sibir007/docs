"""Command-line entry point for the local-docs package."""


def main() -> int:
    """Run the local-docs command.

    The server wiring is implemented in the next refactoring stage. Keeping
    the entry point importable now makes package installation verifiable.
    """
    print("local-docs package is installed; server startup is not implemented yet")
    return 0
