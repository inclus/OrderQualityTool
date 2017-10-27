from node:alpine

RUN mkdir -p /usr/src/app/dashboard/static
WORKDIR /usr/src/app

COPY package.json /usr/src/app/
RUN npm install

COPY webpack.config.js /usr/src/app/
COPY uisrc /usr/src/app/uisrc/
RUN npm run build

FROM python:2.7
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
COPY requirements /usr/src/app/
COPY requirements/*.txt /usr/src/app/requirements/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
COPY --from=0 /usr/src/app/dashboard/static /usr/src/app/dashboard/static/
