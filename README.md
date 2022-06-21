# Leonify

Get the Bank of Sierra Leone approved leones equivalent for EUR, GBP or USD figures.

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

Make a request
```bash
curl http://<your-port>:8000?[eur|gbp|usd]=<amount>
```
