FROM python:3-slim
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY main.py /main.py
ENTRYPOINT ["python3", "/main.py"]
