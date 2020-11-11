FROM python:3.9-alpine
COPY spec.json solution1.py /
VOLUME /data
CMD python3 solution1.py --spec "spec.json"
