import pytest
import threading
import time
import shutil
from http.server import HTTPServer
import requests
from squirrel_server import SquirrelServerHandler
from squirrel_db import SquirrelDB

URL = "http://127.0.0.1:8080"

@pytest.fixture(scope="session", autouse=True)
def server():

    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, SquirrelServerHandler)

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    time.sleep(0.5) # Give the server a moment to start
    yield
    # After all tests are done, shut down the server
    httpd.shutdown()
    httpd.server_close()
    server_thread.join()

@pytest.fixture(scope="function",autouse=True)
def empty_database():
    shutil.copy("empty_squirrel_db.db","squirrel_db.db")
    yield


def add_squirrels_to_db(squirrels_to_add):
    db = SquirrelDB()
    for squirrel in squirrels_to_add:
        db.createSquirrel(squirrel['name'],squirrel['size'])

def describe_Success():
    def describe_GET():
        def test_get_squirrels_return_one_record():
            add_squirrels_to_db([{"name": "Mike", "size": "large"}])
            response = requests.get(f"{URL}/squirrels")
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            expected_data = [{"id": 1, "name": "Mike", "size": "large"}]
            assert response.json() == expected_data
            
        def test_get_squirrels_returns_all_record():
            add_squirrels_to_db([{"name": "Mike", "size": "large"},
                                 {"name": "Joe", "size": "medium"},
                                 {"name": "Frank", "size": "small"}])
            response = requests.get(f"{URL}/squirrels")
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            expected_data = [
                    {"id": 1, "name": "Mike", "size": "large"},
                    {"id": 2, "name": "Joe", "size": "medium"},
                    {"id": 3, "name": "Frank", "size": "small"}]
            assert response.json() == expected_data
        def test_get_by_id_returns_correct_squirrel():
            add_squirrels_to_db([{"name": "Mike", "size": "large"},
                                 {"name": "Joe", "size": "medium"},
                                 {"name": "Frank", "size": "small"}])
            response = requests.get(f"{URL}/squirrels/2")
            assert response.status_code == 200
            assert response.json() == {"id":2, "name": "Joe", "size": "medium"}

    def describe_POST():
        def test_post_squirrel_creates_new_record():
            new_squirrel = {"name": "Mike", "size": "large"}
            response = requests.post(f"{URL}/squirrels", data=new_squirrel)
            assert response.status_code == 201
            get_response = requests.get(f"{URL}/squirrels")
            all_squirrels = get_response.json()
            assert len(all_squirrels) == 1
            expected_data = [{"id":1, "name": "Mike", "size": "large"}]
            assert all_squirrels == expected_data
    def describe_PUT():
        def test_put_updates_squirrels_record_by_id():
            add_squirrels_to_db([{"name": "Mike", "size": "large"},
                                 {"name": "Joe", "size": "medium"},
                                 {"name": "Frank", "size": "small"}])
            updated_record = {"name": "Frank", "size": "medium"}
            response = requests.put(f"{URL}/squirrels/3",data= updated_record)
            assert response.status_code == 204
            get_response = requests.get(f"{URL}/squirrels/3")
            assert get_response.json() == {"id":3,"name": "Frank", "size": "medium"}

    def describe_DELETE():
        def test_delete_by_id_removes_record():
            add_squirrels_to_db([{"name": "Mike", "size": "large"},
                                 {"name": "Joe", "size": "medium"},
                                 {"name": "Frank", "size": "small"}])
            response = requests.delete(f"{URL}/squirrels/2")
            assert response.status_code == 204
            get_response = requests.get(f"{URL}/squirrels")
            all_squirrels = get_response.json()
            assert len(all_squirrels) == 2
            assert all_squirrels[0]["name"] == "Mike"
            assert all_squirrels[1]["name"] == "Frank"

def describe_Failure():
    def describe_GET_FAIL():
        def test_get_non_existent_squirrel_returns_404():
            response = requests.get(f"{URL}/squirrels/999")
            assert response.status_code == 404
        
        def test_get_non_existent_endpoint_returns_404():
            response = requests.get(f"{URL}/squirtle")
            assert response.status_code == 404
        
    def describe_POST_FAIL():
        def test_post_non_existent_endpoint_returns_404():
            response = requests.post(f"{URL}/squirtle", data={"name":"Frank","size":"large"})
            assert response.status_code == 404

        def test_post_to_specific_squirrel_id_returns_404():
            add_squirrels_to_db([{"name": "Frank", "size": "small"}])
            response = requests.post(f"{URL}/squirrels/1", data={"name": "George","size": "medium"})
            assert response.status_code == 404

    def describe_PUT_FAIL():

        def test_put_non_existent_squirrel_returns_404():
            response = requests.put(f"{URL}/squirrels/999", data={"name": "Frank", "size": "small"})
            assert response.status_code == 404
        
        def test_put_non_existent_endpoint_returns_404():
            response = requests.put(f"{URL}/squirtle", data={"name":"George", "size": "small"})
            assert response.status_code == 404
        def test_put_to_squirrel_collection_returns_404():
            response = requests.put(f"{URL}/squirrels", data={"name": "George","size": "small"})
            assert response.status_code == 404


    
    def describe_DELETE_FAIL():

        def test_delete_non_existent_squirrel_returns_404():
            response = requests.delete(f"{URL}/squirrels/999")
            assert response.status_code == 404

        def test_delete_non_existent_endpoint_returns_404():
            response = requests.delete(f"{URL}/squirtle")
            assert response.status_code == 404

        def test_delete_to_squirrel_collection_returns_404():
            response = requests.delete(f"{URL}/squirrels")
            assert response.status_code == 404
