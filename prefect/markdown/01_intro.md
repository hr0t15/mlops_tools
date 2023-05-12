# Prefect 入門(1) : 基礎編

## Prefectのワークフロー構成要素: task と flow

Prefectでワークフローを組むには, FlowとTaskが基本的な骨組みになります。

- Task: ワークフローを構成する処理の単位(ex. ETLのE, T, Lの部分)
- Flow: Taskの組み合わせたワークフロー全体(ex. ETL全体)

TaskとFlowに対して、オプション機能を追加していく流れになります。

### flowの

Prefectを使い始める最も簡単な方法は、`flow`をインポートし、`@flow`デコレータを使ってPython関数にアノテーションを付けることです。

以下のコードをコードエディター、Jupyter Notebook、またはPython REPLに入力します。

```python
# intro01.py
from prefect import flow

@flow
def hello():
    print("Hello, Prefect!")
    return 42

print(hello())
```

Prefectのフローを手動で実行するには、アノテーションされた関数（この場合はmy_favorite_function()）を呼び出すだけで、簡単に実行できます。

このコードをPythonスクリプトで実行すると、次のような出力が得られます：

```
14:08:17.971 | INFO    | prefect.engine - Created flow run 'topaz-panda' for flow 'hello'
Hello, Prefect!
14:08:18.210 | INFO    | Flow run 'topaz-panda' - Finished in state Completed()
42
```

期待される出力である"Hello, Prefect!"を取り巻くログメッセージに注目してください。最後に、関数が返した値が出力されます。

関数に`@flow`デコレーターを追加することで、関数呼び出しがフロー実行を作成します。
Prefectオーケストレーションエンジンは、フローコードがどこで実行されても、フローとタスクの状態を管理します。


### パラメータでフローを実行

Pythonの関数と同様に、引数を渡すことができます。  
フロー関数に定義された位置引数やキーワード引数は、パラメータと呼ばれます。デモンストレーションとして、以下のコードを実行してみてください：

```python
# intro02.py
import requests
from prefect import flow

@flow
def call_api(url):
    return requests.get(url).json()

api_result = call_api("http://time.jsontest.com/")
print(api_result)
```
有効なURLをパラメータとして渡し、`call_api()`フローを実行しましょう。  
この場合、レスポンスに有効なJSONを返すべきAPIにGETリクエストを送信しています。  
APIコールによって返された辞書を出力するために、`print`関数でラップしています。

```
14:15:24.810 | INFO    | prefect.engine - Created flow run 'conscious-gorilla' for flow 'call-api'
14:15:25.549 | INFO    | Flow run 'conscious-gorilla' - Finished in state Completed()
{'date': '05-12-2023', 'milliseconds_since_epoch': 1683900925363, 'time': '02:15:25 PM'}
```

### タスクで基本的なフローを実行

それでは、フローにタスクを追加して、より細かいレベルでのオーケストレーションや監視ができるようにしましょう。

タスクは、フロー内で実行される明確な作業部分を表す関数です。タスクの使用は必須ではありません。ワークフローのすべてのロジックをフロー自体に含めることができます。  
しかし、ビジネスロジックをより小さなタスク単位にカプセル化することで、よりきめ細かい観測が可能になり、特定のタスクの実行方法を制御でき（並列実行を活用できる可能性がある）、フローやサブフロー間でタスクを再利用することができます。

タスクの作成と追加は、フローとまったく同じパターンで行います。`task`をインポートし、`@task`デコレータを使用して、関数をタスクとしてアノテーションします。

hello, world風のタスクとフローを導入する。

```python
# intro03.py
from prefect import flow, task

@task
def hello(param):
    print(f"Hello, {param}!")


@flow
def hello_param_flow(param):
    hello_world = hello(param)
    return hello_world

print(hello_flow("Prefect"))
```

hello, world風のタスクを2つにわける。

```python
# intro04.py
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
```

先ほどの`call_api()`の例で、実際のHTTPリクエストを独自のタスクに移動してみましょう。

```python
# intro05.py
import requests
from prefect import flow, task

@task
def call_api(url):
    response = requests.get(url)
    print(response.status_code)
    return response.json()

@flow
def api_flow(url):
    fact_json = call_api(url)
    return fact_json

print(api_flow("https://catfact.ninja/fact"))
```

そして、以前と同じようにフロー関数（現在は`api_flow()`と呼ばれています）を呼び出し、印刷された出力を見ることができます。Prefectは、すべての中間状態を管理します。

```
14:28:35.573 | INFO    | prefect.engine - Created flow run 'zealous-limpet' for flow 'api-flow'
14:28:35.810 | INFO    | Flow run 'zealous-limpet' - Created task run 'call_api-0' for task 'call_api'
14:28:35.812 | INFO    | Flow run 'zealous-limpet' - Executing 'call_api-0' immediately...
200
14:28:36.979 | INFO    | Task run 'call_api-0' - Finished in state Completed()
14:28:37.031 | INFO    | Flow run 'zealous-limpet' - Finished in state Completed()
{'fact': 'Approximately 40,000 people are bitten by cats in the U.S. annually.', 'length': 68}
```

もちろん、他のタスクから入力を受けたり、他のタスクに入力を渡したりするタスクも作成可能です。

```python
# intro06.py
import requests
from prefect import flow, task

@task
def call_api(url):
    response = requests.get(url)
    print(response.status_code)
    return response.json()

@task
def parse_fact(response):
    fact = response["fact"]
    print(fact)
    return fact

@flow
def api_flow(url):
    fact_json = call_api(url)
    fact_text = parse_fact(fact_json)
    return fact_text

api_flow("https://catfact.ninja/fact")
```

```
14:30:26.231 | INFO    | prefect.engine - Created flow run 'ebony-potoo' for flow 'api-flow'
14:30:26.469 | INFO    | Flow run 'ebony-potoo' - Created task run 'call_api-0' for task 'call_api'
14:30:26.470 | INFO    | Flow run 'ebony-potoo' - Executing 'call_api-0' immediately...
200
14:30:27.770 | INFO    | Task run 'call_api-0' - Finished in state Completed()
14:30:27.817 | INFO    | Flow run 'ebony-potoo' - Created task run 'parse_fact-0' for task 'parse_fact'
14:30:27.818 | INFO    | Flow run 'ebony-potoo' - Executing 'parse_fact-0' immediately...
Some Siamese cats appear cross-eyed because the nerves from the left side of the brain go to mostly the right eye and the nerves from the right side of the brain go mostly to the left eye. This causes some double vision, which the cat tries to correct by “crossing” its eyes.
14:30:27.956 | INFO    | Task run 'parse_fact-0' - Finished in state Completed()
14:30:28.008 | INFO    | Flow run 'ebony-potoo' - Finished in state Completed()
```

