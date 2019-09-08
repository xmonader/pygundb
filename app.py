from gundb.server import app


print(app.url_map)

if __name__ == "__main__":
    app.run(port=8000)
