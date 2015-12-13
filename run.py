from app import create_app

app1 = create_app("default", "app1")
app2 = create_app("default", "app2")

if __name__ == "__main__":
    app1.run(port=5000)
