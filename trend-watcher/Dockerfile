FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir pytrends anthropic
COPY . .
CMD ["sh", "-c", "python collect_instagram.py && python collect_gtrends.py && python make_digest.py --email"]
