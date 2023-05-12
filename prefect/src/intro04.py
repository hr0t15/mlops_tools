from prefect import flow, task

@task
def get_param():
    return "world"

@task
def hello(param):
    print(f"Hello, {param}!")


@flow
def hello_flow():
    param = get_param()
    hello_world = hello(param)
    return hello_world

print(hello_flow())
