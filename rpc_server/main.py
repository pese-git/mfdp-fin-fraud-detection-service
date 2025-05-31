from src.rpc_server import RPCServer
from src.database.database import engine

if __name__ == "__main__":
    rpc_server = RPCServer(engine=engine)
    rpc_server.start()