from prefect import flow

@flow
def hello():
    print("Hello, Prefect!")
    return 42

print(hello())
