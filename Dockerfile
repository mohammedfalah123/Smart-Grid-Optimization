FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app:$PYTHONPATH \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir pytest==7.4.0
RUN pip install --no-cache-dir numpy==1.24.3 pandas==2.0.3
RUN pip install --no-cache-dir pandapower==2.12.0
RUN python -c "import pandapower as pp; import pandapower.networks as pn; net = pn.case9(); print('✅ Pandapower works!')"
RUN pip install --no-cache-dir \
    scipy==1.11.1 \
    matplotlib==3.7.2 \
    plotly==5.17.0 \
    mealpy==3.0.1 \
    gradio==4.44.1 \
    huggingface-hub==0.25.2

COPY --chown=user requirements.txt $HOME/app/requirements.txt
COPY --chown=user . $HOME/app
CMD ["python", "app.py"]
