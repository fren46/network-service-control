FROM gcr.io/airspot/ruleset-image-base:0.8.1

ADD ./app /app

# nice to have an interactive shell
RUN pip install ipython websocket-client
RUN pip install ipython
ADD ipython_config.py /root/.ipython/profile_default/

RUN pip install krules-subjects-storage-redis==0.8.1
# RUN pip install krules-subjects-storage-mongodb==0.8
