# RESTinstance

    PYTHONPATH="src" python -c 'from REST import REST; res = REST("localhost:8080").get("/users/1"); REST.print(res["body"])'
