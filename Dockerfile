FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y fonts-noto-core fonts-noto-cjk fontconfig libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 && \
    fc-cache -fv && \
    ldconfig && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple && \
    python3 -m pip install uv -i https://mirrors.aliyun.com/pypi/simple && \
    # 【修改这里】为 uv 显式加上 -i 参数，指定阿里云镜像源
    uv pip install --system -i https://mirrors.aliyun.com/pypi/simple 'mineru>=4.0,<5' && \
    python3 -m pip cache purge

# 【删掉下面这行！】模型现在在宿主机上，不用重新下载了
# RUN mineru-kit models download --tier standard --source modelscope

ENTRYPOINT ["/bin/bash", "-c", "export MINERU_MODEL_SOURCE=local && exec \"$@\"", "--"]