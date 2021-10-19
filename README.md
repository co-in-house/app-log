# app-bff

`pip3 install -r requirements.txt`

or


1. create image
   - `docker build -t app-bff:0.0.1 .`
2. create container
   - `docker run -d --name app-bff-container -p 80:80 app-bff:0.0.1`
3. get container id
   - `docker ps  | grep app-bff`
4. show logs
   - `docker logs <ContainerId> -f`