def get_version() -> str:
    """
    Retrieves the version number from the pyproject.toml file.

    Returns:
        str: The version number.
    """
    with open("pyproject.toml", encoding="utf-8") as f:
        for line in f:
            if "version" in line:
                return line.split("=")[1].strip().strip('"')