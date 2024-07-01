# Load docker image with Java
FROM python:3.8-alpine AS build
# Build stage
RUN apk add --no-cache python3-dev openssl-dev libffi-dev libc-dev gcc libsodium-dev && pip3 install --upgrade pip
COPY requirements.txt /requirements.txt
WORKDIR /
RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install -r requirements.txt

# Final stage
# FROM python:3.8-alpine
# RUN apk add --no-cache libsodium-dev
# COPY --from=build /usr/local /usr/local
# COPY src /home/python/src
# COPY topologies /home/python/topologies
# WORKDIR /home/python
# CMD python -u src/run.py $PID $TOPOLOGY $ALGORITHM -docker


FROM python:3.8-alpine
RUN apk add --no-cache libsodium-dev
COPY --from=build /usr/local /usr/local
COPY src /home/python/src
COPY topologies /home/python/topologies
WORKDIR /home/python
# CMD python -u src/algorithms/stormGarbage/gino/main.py $PID $TOPOLOGY $ALGORITHM -docker
# CMD echo "python -u src/algorithms/stormGarbage/gino/main.py $PID $TOPOLOGY $ALGORITHM -docker"
# node1-1  | python -u src/algorithms/stormGarbage/gino/main.py 1 topologies/blockchain.yaml blockchain -docker
# node0-1  | python -u src/algorithms/stormGarbage/gino/main.py 0 topologies/blockchain.yaml blockchain -docker

CMD python -u src/main.py $PID $TOPOLOGY $ALGORITHM -docker
