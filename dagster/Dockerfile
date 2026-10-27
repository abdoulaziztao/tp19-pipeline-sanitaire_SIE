FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY assets.py .
ENV DAGSTER_HOME=/dagster_home
RUN mkdir -p /dagster_home
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000", "-f", "assets.py"]