from prefect import flow, task

@task
def hello(param):
    print(f"Hello, {param}!")


@flow
def hello_param_flow(param):
    hello_world = hello(param)
    return hello_world

print(hello_param_flow("Prefect"))
