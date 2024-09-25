ARG PYTHON_VERSION=3.8-slim
FROM python:${PYTHON_VERSION}

USER root

WORKDIR /app

COPY . /app

#Installing all required modules
RUN python -m pip install --no-cache-dir -r requirements.txt

EXPOSE 7755

#Starting Server
CMD ["bash", "run.sh"]