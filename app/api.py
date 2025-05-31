from fastapi import FastAPI
from routes.home import home_route
from routes.user import user_route
from routes.event import event_router
from database.database import init_db
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.include_router(home_route)
app.include_router(user_route, prefix='/user')
app.include_router(event_router, prefix='/event')

origins = ["*"] 
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.on_event("startup") 
def on_startup():
    init_db()

if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)