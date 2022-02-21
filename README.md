# Leonify

This application's index endpoint returns the leones equivalent of the passed
EUR, GBP or USD value.

To get started, ensure you have poetry install and run,
```bash
poetry install
make devserver
```

If you have docker installed,
```bash
docker build -t leonify:<your-tag> .
docker run -p <your-port>:8000 -it leonify:<your-tag>
```
