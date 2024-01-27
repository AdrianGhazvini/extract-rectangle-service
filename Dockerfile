FROM python:3.8-slim
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir flask opencv-python-headless numpy requests
EXPOSE 5000
ENV FLASK_APP=rect_extraction.py
CMD ["flask", "run", "--host=0.0.0.0"]
