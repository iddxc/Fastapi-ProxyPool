from uvicorn import run
from fastapi import FastAPI
from conf.settings import IS_DEV, API_HOST, API_PORT
from proxypool.storages import store

app = FastAPI()

@app.get('/proxy')
async def get_proxy():
    proxy = store.random()
    return proxy.string()



class Server(object):
    def run(self):
        run(app="server.app:app", host=API_HOST, port=API_PORT, reload=True)


if __name__ == '__main__':
    Server().run()