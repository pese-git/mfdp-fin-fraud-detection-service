FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

# Установим системные зависимости (если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Установим torch и зависимости
RUN pip install torch==2.7.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install torch-geometric==2.6.1
RUN pip install torch-cluster==1.6.3 -f https://data.pyg.org/whl/torch-2.7.0+cpu.html

# Проверка
RUN python -c "import torch; print(torch.__version__)"

COPY . .

CMD ["python", "main.py"]
