# Redis lab

DB laboratory work

## Installation

### Linux

1. Install and run redis

```$ sudo apt-get install redis```

```$ redis-server```

2. Clone this repo

```$ git clone https://github.com/somnoynadno/redis-lab```

```$ cd redis-lab```

3. Install python requirements

```$ pip3 install -r requirements.txt```

4. Run the application 

```$ python3 main.py```

Available on localhost:8888

### Docker

0. Create virtual network

```$ docker network create redis-lab-network```

1. Pull and build redis image

```$ sudo docker pull redis```

```$ sudo docker run --name gredis -d --network=redis-lab-network redis```

2. Build image

```$ sudo docker build -t redis-lab .```

3. Run daemon (notice the REDIS_HOST env variable)

```$ sudo docker run -it --rm --name redis-lab -p 9001:8888 --network=redis-lab-network -e REDIS_HOST=gredis -d redis-lab```

Available on 0.0.0.0:9001

## Presentation

https://docs.google.com/presentation/d/17beUc-1yKHs5BBDGU7un4ppMDTBs8xnKa7Ux1BdyMKs/edit?usp=sharing