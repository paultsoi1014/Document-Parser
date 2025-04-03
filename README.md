# Structure Aware Document Parser

## Table of Contents

- [Overview](#Overview)
- [Prerequisites](#Prerequisites)
- [Installation](#installation)
- [Usage](#usage)

## Overview 
A backbone that utilize a series of object detection models to parse documents 
for various application including structure aware OCR or for RAG

## Prerequest
Before installing and using the document parser, ensure that the following components are set up and running:

### 1. Florence-2 Vision Model
Florence-2 is an advanced vision foundation model used for visual understanding. Follow these steps to set it up:
```bash
# Make sure git-lfs is installed (https://git-lfs.com)
git lfs install
git clone https://huggingface.co/microsoft/Florence-2-base
```

## Installation
### 1. Clone the repository:
```bash
git clone https://github.com/paultsoi1014/Document-Parser.git
```
### 2. Navigate to the project directory:
```bash
cd document_parser
```
### 3. Create and activate a virtual environment:
#### Option 1: Using `venv` (Python Standard Library)
```bash
python -m venv venv
source venv/bin/activate 
```
#### Option 2: Using `conda` (Python 3.11)
```bash
conda create --name myenv python=3.11
conda activate myenv
```

### 4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
### 1. Set Up Environment Variables
Copy the example environment file and configure your own `.env`:
```bash
cp .env.example .env
```
Edit the `.env` file to update necessary configurations.

### 2. Running the API Server
#### Option 1: Run Directly
```python
python api_server.py
```
#### Option 2: Run with Docker-Compose
```bash
docker compose up -d --build
```

### 4. Parse the document through running the example 
```python
python example/parse.py
```





