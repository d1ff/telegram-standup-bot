#
# ---- Base Node ----
FROM python:3.7.0 AS base
# container info
LABEL Description="Simple Telegram Standup bot Logger"
# explicitly declare locale
ENV LANG=C.UTF-8
# set working directory
WORKDIR /app
# Upgrade pip
RUN pip install --upgrade pip

#
# ---- Dependencies ----
FROM base AS deps

RUN pip install poetry
RUN poetry config virtualenvs.create false
# copy requirements folder
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN poetry install

#
# ---- Development ----
FROM deps AS dev
# set envs
ENV HOST 0.0.0.0
ENV PORT 8000
# expose port and define CMD
EXPOSE ${PORT}
#define command line
CMD uvicorn --host ${HOST} --port ${PORT} telegram_standup_logger:app
# copy app sources
COPY . .
