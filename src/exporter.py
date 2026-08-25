import os


def write_csv(path, rows):
    """Scrive rows in un nuovo file CSV. Fallisce se il file esiste già (scrittura esclusiva)."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open(path, flags)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(",".join(row) + "\n")
