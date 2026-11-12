import os


def write_csv(path, rows):
    """Writes rows to a new CSV file. Fails if the file already exists (exclusive write)."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open(path, flags)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(",".join(row) + "\n")
