FROM alpine
RUN mkdir /gschmock
COPY . /gschmock/
COPY entry.sh /gschmock/entry.sh
RUN apk update && apk add python3 py3-pip make
COPY branchweb /branchweb/
RUN pip install setuptools requests && pip install bcrypt
RUN cd /branchweb/ && python3 setup.py sdist && pip install dist/branchweb-1.0.tar.gz
RUN cd /branchlog/ && python3 setup.py sdist && pip install dist/branchlog-1.0.tar.gz
CMD /gschmock/entry.sh
EXPOSE 8080/tcp
