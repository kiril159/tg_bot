FROM bitnami/python:3.7-debian-11

ENV TIMEZONE="Europe/Moscow"
ENV APP_HOME=/app

RUN rm -rf /etc/localtime \
    && ln -s /usr/share/zoneinfo/$TIMEZONE /etc/localtime \
    && echo "${TIMEZONE}" > /etc/timezone \
    && adduser www --uid 1000 --disabled-password \
    && mkdir -p -m 0755 /app \
    && chown www:www /app \
    && apt-get update \
    && apt-get -q -y install ca-certificates

ADD requierments.txt $APP_HOME/requierments.txt

ENV PATH $APP_HOME/.local/bin:${PATH}

WORKDIR $APP_HOME

RUN pip install -r requierments.txt

USER www

COPY --chown=www:www main.py $APP_HOME/
COPY --chown=www:www prompt.txt $APP_HOME/
COPY --chown=www:www prompt2.txt $APP_HOME/

CMD ["python3.7", "/app/main.py"]
