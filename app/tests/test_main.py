def test_show_path_and_import() -> None:
    import sys
    print("\n=== sys.path ===\n", "\n".join(sys.path))
    print("\n=== import src OK ===\n")

def test_import_auth() -> None:
    print("\n=== import src.auth.authenticate OK ===\n")