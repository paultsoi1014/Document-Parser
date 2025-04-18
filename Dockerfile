FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# Update package lists and install Python 3.10, pip, and essential tools
RUN apt-get update -y && \
    apt-get install -y software-properties-common wget git ffmpeg libsm6 libxext6 && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update -y && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN python3.10 -m pip install --upgrade pip

# Set Python 3.10 as the default Python
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Set working directory and copy app files
WORKDIR /app
COPY . . 

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Clone florence repository 
RUN mkdir -p /model
RUN git clone https://huggingface.co/microsoft/Florence-2-base /model

# Install Python dependencies with uv tool
RUN uv pip install --system -r requirements.txt

CMD ["python3", "api_server.py"]