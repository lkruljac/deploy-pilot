FROM python:3.12-alpine

ARG GIT_SHA=unknown
ARG GIT_BRANCH=unknown
ARG BUILD_TIME=unknown

ENV GIT_SHA=$GIT_SHA \
    GIT_BRANCH=$GIT_BRANCH \
    BUILD_TIME=$BUILD_TIME \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY src/ ./

RUN adduser -D -u 10001 app
USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1

CMD ["python", "-u", "app.py"]
