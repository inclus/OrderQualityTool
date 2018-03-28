from node:alpine as node

RUN mkdir -p /usr/src/app/dashboard/static
WORKDIR /usr/src/app

COPY package.json package-lock.json .eslintrc /usr/src/app/
RUN npm install

COPY webpack.config.js /usr/src/app/
COPY uisrc /usr/src/app/uisrc/
RUN npm run build

FROM python:2.7
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV PHANTOM_JS_VERSION 2.1.1-linux-x86_64
RUN apt-get update && apt-get install -y --no-install-recommends curl bzip2 libfreetype6 libfontconfig
RUN curl -sSL "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-$PHANTOM_JS_VERSION.tar.bz2" | tar xjC /
RUN ln -s "/phantomjs-$PHANTOM_JS_VERSION/bin/phantomjs" /usr/local/bin/phantomjs

COPY requirements.txt /usr/src/app/
COPY requirements /usr/src/app/
COPY requirements/*.txt /usr/src/app/requirements/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
COPY --from=node /usr/src/app/dashboard/static /usr/src/app/dashboard/static/
RUN python manage.py collectstatic --no-input
