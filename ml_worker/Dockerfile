#FROM python:3.10-slim
FROM nvidia/cuda:11.8.0-base-ubuntu22.04

WORKDIR /app

COPY requirements.txt /app/

# [1] Установить системные dev-пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends python3.10
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip
    
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# После основного requirements
#RUN pip install torch==2.7.0
#RUN pip install torch-geometric==2.6.1
#RUN pip install torch-cluster==1.6.3

RUN pip3 --no-cache-dir install torch==2.7.0 --index-url https://download.pytorch.org/whl/cu118

# Установка PyG и зависимых пакетов
RUN pip3 install torch_geometric==2.6.1

RUN pip3 install torch-cluster==1.6.3 \
    -f https://data.pyg.org/whl/torch-2.7.0+cu118.html

#
#RUN pip3 install torch-geometric==2.6.1 torch-cluster==1.6.3 \
#    -f https://data.pyg.org/whl/torch-2.7.0+cu118.html
#
#RUN pip3 install torch-geometric==2.6.1 torch_cluster==1.6.3 \
#    -f https://data.pyg.org/whl/torch-2.7.0+cpu.html 

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN python -c "import torch; print(torch.__version__)"

CMD ["python3", "main.py"]