from fastapi.testclient import TestClient

def test_home_request(client: TestClient):
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "success"}
    
def test_get_events(client: TestClient):
    response = client.get("/event/")
    assert response.status_code == 200
    assert response.json() == []
    
def test_create_event(client: TestClient):
    event = {"id": 0, 
            "title": "title", 
            "image": "img", 
            "description": "description",  
            "tags": ['test1', 'test2'],
            "location": 'loc',
            "creator": 'user'}
    response = client.post("/event/new", json=event)

    assert response.status_code == 200
    assert response.json() == {"message": "Event created successfully"}
    
def test_clear_events(client: TestClient):
    response = client.delete("/event/")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Events deleted successfully"}