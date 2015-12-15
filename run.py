from app import create_app

app1 = create_app("default", "app1")
app2 = create_app("default", "app2")

if __name__ == "__main__":
    app1.run(port=5000)

### Reference: Some of the code referenced from book <Flask Web Development> by Niguel Grinberg ###
