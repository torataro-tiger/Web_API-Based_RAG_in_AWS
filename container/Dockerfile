FROM public.ecr.aws/lambda/python:3.12

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py settings.py ${LAMBDA_TASK_ROOT}/

CMD [ "app.handler" ]
