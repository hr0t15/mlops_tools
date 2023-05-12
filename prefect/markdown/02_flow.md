
# フロー（Flows）

フローは、Prefectの最も基本的なオブジェクトです。  
フローは、Prefect エンジンの他の側面を参照することなく、対話、表示、および実行が可能な唯一の Prefect 抽象関数です。  
フローは、ワークフローロジックのコンテナであり、ユーザーがワークフローの状態と対話し、推論することができます。  
Pythonでは、1つの関数として表現されます。

## フローの概要
フローは関数のようなものです。入力を受け取り、作業を行い、出力を返すことができます。実際、`@flow`デコレータを追加することで、任意の関数をPrefectフローにすることができます。関数がフローになると、その動作が変化し、以下のような利点があります：

- 状態遷移がAPIに報告され、フローランを観察することができる。
- 入力引数の型を検証することができる。
- 失敗時の再試行が可能
- タイムアウトを設定することで、意図しない長時間のワークフローを防ぐことができます。

また、Prefectの自動ロギングを利用して、実行時間、タスクタグ、最終状態など、[フローラン](https://docs.prefect.io/latest/concepts/flows/#flow-runs)に関する詳細を記録することができます。

すべてのワークフローは、フローのコンテキスト内で定義されます。フローは、タスクへの呼び出しだけでなく、他のフローへの呼び出しも含むことができ、この文脈では「サブフロー」と呼んでいます。フローはモジュール内で定義し、フロー定義のサブフローとして使用するためにインポートすることができます。

フローはデプロイメントに必要です。すべてのデプロイメントは、フロー実行のエントリポイントとして特定のフローを指します。

タスクはフローから呼び出す必要がある

すべてのタスクは、フロー内から呼び出す必要があります。タスクは、他のタスクから呼び出すことはできません。

## フローラン

フローランは、フローを1回実行することを表します。

フローを呼び出すことで、フローランを作成することができます。例えば、Pythonスクリプトを実行したり、フローを対話型セッションにインポートしたりすることで作成できます。

また、以下の方法でもフローランを作成できます：

- Prefect Cloud またはローカルで実行する Prefect サーバー上にデプロイメントを作成する。
- スケジュール、Prefect UI、またはPrefect APIを使用して、デプロイメント用のフロー実行を作成する。

フローを実行すると、Prefect APIがフロー実行を監視し、観測可能なようにフロー実行の状態をキャプチャします。

タスクや追加フローを含むフローを実行する場合、Prefectは、親フローランに対する各子ランの関係を追跡します。

![Prefect UI](https://docs.prefect.io/latest/img/ui/prefect-dashboard.png)

## フローを書く

ほとんどのユースケースでは、`@flow`デコレータを使用してフローを指定することをお勧めします：

```python
from prefect import flow

@flow
def my_flow():
    return
```

フローは、名前によって一意に識別されます。フローには、`name` パラメータ値を指定することができます。  
`name`を指定しない場合、Prefectはフロー関数名を使用します。

```python
from prefect import flow

@flow(name="My Flow")
def my_flow():
    return
```

フローは、タスクを呼び出して特定の作業をさせることができます：

```python
from prefect import flow, task

@task
def print_hello(name):
    print(f"Hello {name}!")

@flow(name="Hello Flow")
def hello_world(name="world"):
    print_hello(name)
```

フローとタスク

すべてのコードを1つのフロー関数にまとめても、Prefectはそれを喜んで実行します！

しかし、ワークフローのコードをフローやタスクの単位で整理することで、リトライや実行状態の詳細な可視化、個々のタスクの状態に関係なく最終状態を決定する機能など、Prefectの機能を利用することができます。

また、ワークフローのロジックを1つのフロー関数にまとめた場合、コードの1行でも失敗すると、フロー全体が失敗し、最初からやり直さなければなりません。これは、コードを複数のタスクに分割することで回避することができます。

Prefect のワークフローには、1 つのプライマリ関数、エントリポイント @flow 関数が必要です。この関数から、他のタスク、サブフロー、通常の Python 関数を呼び出すことができます。エントリポイントのフロー関数には、ワークフローの他の場所で使用されるパラメータを渡すことができ、エントリポイントのフロー関数の最終状態が、ワークフローの最終状態を決定します。

Prefectは「スモールタスク」を推奨しており、各タスクはワークフローの1つの論理ステップを表しています。これにより、Prefect はタスクの失敗をより適切に抑制することができます。


## フローの設定
Flowは、デコレータに引数を渡すことで、多くの設定を行うことができます。フローは、以下のオプション設定を受け付けます。

|引数 |説明 |
|- |- |
|`description` |フローの説明（オプションの文字列）です。指定しない場合は、装飾された関数のdocstringから説明が取得されます。|
|`name` |フローのオプションの名前。提供されない場合、名前は関数から推論される。|
|`retries` |フローランに失敗した場合に再試行する回数（オプション）。|
|`retry_delay_seconds` |失敗した後にフローを再試行するまでの待機秒数（オプション）。`retries` が 0 でない場合のみ適用されます。|
|`flow_run_name` | この名前は、フローのパラメータを変数とする文字列テンプレートとして提供することができます。また、この名前は、文字列を返す関数として提供することもできます。|
|`task_runner` |`.submit()`タスクの実行時にフロー内で使用するオプションのタスクランナーです。`.submit()`タスクを実行する際に、フロー内のタスク実行に使用するオプションのタスクランナー。|
|`timeout_seconds` |フローの最大実行時間を示す秒数（オプション）。フローがこのランタイムを超えた場合、失敗とマークされます。フローランは、次のタスクが呼び出されるまで継続することができます。|
|`validate_parameters` |フローに渡されるパラメータがPydanticによって検証されるかどうかを示すブール値です。デフォルトは`True`です。|
|`version` |フローのバージョン文字列（オプション）。提供されない場合、ラップされた関数を含むファイルのハッシュとしてバージョン文字列を作成しようとします。ファイルが見つからない場合、バージョンはNULLになります。|

例えば、フローに`name`値を指定することができます。ここでは、オプションのdescription引数も使用し、デフォルトでないタスクランナーを指定しています。

```python
from prefect import flow
from prefect.task_runners import SequentialTaskRunner

@flow(name="My Flow",
      description="My flow using SequentialTaskRunner",
      task_runner=SequentialTaskRunner())
def my_flow():
    return
```

また、flow関数のdocstringとしてdescriptionを提供することもできます。

```python
@flow(name="My Flow",
      task_runner=SequentialTaskRunner())
def my_flow():
    """My flow using SequentialTaskRunner"""
    return
```

この設定には、オプションでフローのパラメータへのテンプレート参照を含む文字列を受け入れることができます。この設定は、オプションでフローのパラメータへのテンプレート参照を含むことができる文字列を受け入れます。この名前は、ここで見られるように、Pythonの標準の文字列書式構文を使ってフォーマットされます：

```python
import datetime
from prefect import flow

@flow(flow_run_name="{name}-on-{date:%A}")
def my_flow(name: str, date: datetime.datetime):
    pass

# creates a flow run called 'marvin-on-Thursday'
my_flow(name="marvin", date=datetime.datetime.utcnow())
```

さらに、この設定には、フローランの名前を文字列で返す関数も使えます：

```python
import datetime
from prefect import flow

def generate_flow_run_name():
    date = datetime.datetime.utcnow()

    return f"{date:%A}-is-a-nice-day"

@flow(flow_run_name=generate_flow_run_name)
def my_flow(name: str):
    pass

# creates a flow run called 'Thursday-is-a-nice-day'
my_flow(name="marvin")
```

フローに関する情報へのアクセスが必要な場合は、`prefect.runtime`モジュールを使用します。例えば、以下のようになります：

```python
from prefect import flow
from prefect.runtime import flow_run

def generate_flow_run_name():
    flow_name = flow_run.flow_name

    parameters = flow_run.parameters
    name = parameters["name"]
    limit = parameters["limit"]

    return f"{flow_name}-with-{name}-and-{limit}"

@flow(flow_run_name=generate_flow_run_name)
def my_flow(name: str, limit: int = 100):
    pass

# creates a flow run called 'my-flow-with-marvin-and-100'
my_flow(name="marvin")
```

`validate_parameters`は、入力値が関数の注釈付き型に適合していることをチェックすることに注意してください。  
可能であれば、値は正しい型に強制的に変換されます。例えば、パラメータが`x: int`と定義され、"5"が渡された場合、それは5と解決されます。


## ロジックをタスクに分離する

最もシンプルなワークフローは、ワークフローのすべての作業を行う`@flow`関数だけです。

```python
from prefect import flow

@flow(name="Hello Flow")
def hello_world(name="world"):
    print(f"Hello {name}!")

hello_world("Marvin")
```

このフローを実行すると、次のような出力が表示されます：

```
15:11:23.594 | INFO    | prefect.engine - Created flow run 'benevolent-donkey' for flow 'hello-world'
15:11:23.594 | INFO    | Flow run 'benevolent-donkey' - Using task runner 'ConcurrentTaskRunner'
Hello Marvin!
15:11:24.447 | INFO    | Flow run 'benevolent-donkey' - Finished in state Completed()
```

より良い方法は、フローの特定の作業を行う`@task`関数を作成し、`@flow`関数をアプリケーションのフローを編成する指揮者として使用することです：

```python
from prefect import flow, task

@task(name="Print Hello")
def print_hello(name):
    msg = f"Hello {name}!"
    print(msg)
    return msg

@flow(name="Hello Flow")
def hello_world(name="world"):
    message = print_hello(name)

hello_world("Marvin")
```

このフローを実行すると、次のような出力が表示され、作業がタスク実行にカプセル化されていることがわかります。

```
15:15:58.673 | INFO    | prefect.engine - Created flow run 'loose-wolverine' for flow 'Hello Flow'
15:15:58.674 | INFO    | Flow run 'loose-wolverine' - Using task runner 'ConcurrentTaskRunner'
15:15:58.973 | INFO    | Flow run 'loose-wolverine' - Created task run 'Print Hello-84f0fe0e-0' for task 'Print Hello'
Hello Marvin!
15:15:59.037 | INFO    | Task run 'Print Hello-84f0fe0e-0' - Finished in state Completed()
15:15:59.568 | INFO    | Flow run 'loose-wolverine' - Finished in state Completed('All states completed.')
```


## フローの構成

サブフロー実行は、フロー関数が他のフローラン内部で呼び出されたときに作成されます。  
主フローは「親」フローです。親フローの中に作られるフローは、「子」フローまたは「サブフロー」です。

サブフローランは、通常のフローランと同じように動作する。バックエンドでは、フローが個別に呼び出されたかのように、フロー実行の完全な表現があります。サブフローが開始されると、サブフロー内のタスクのために新しいタスクランナーが作成されます。サブフローが完了すると、タスクランナーはシャットダウンされます。

サブフローは、完了するまで親フローランをブロックします。ただし、非同期サブフローは、AnyIOタスク・グループまたはasyncio.gatherを使用して並行して実行することができます。

サブフローが通常のフローと異なるのは、渡されたタスクの先物をデータに解決する点です。これにより、親フローから子フローに簡単にデータを渡すことができます。

子フローと親フローの関係は、親フローに特別なタスクランを作成することで追跡されます。このタスク実行は、子フローラン状態を反映します。

サブフローを表すタスクは、`state_details`に`child_flow_run_id`フィールドが存在するため、そのように注釈される。サブフローは、`state_details`に`parent_task_run_id`フィールドが存在することで特定することができる。

同じファイル内に複数のフローを定義することができます。ローカルで実行する場合でも、デプロイメントで実行する場合でも、フロー実行のエントリポイントになるフローを指定する必要があります。

```python
from prefect import flow, task

@task(name="Print Hello")
def print_hello(name):
    msg = f"Hello {name}!"
    print(msg)
    return msg

@flow(name="Subflow")
def my_subflow(msg):
    print(f"Subflow says: {msg}")

@flow(name="Hello Flow")
def hello_world(name="world"):
    message = print_hello(name)
    my_subflow(message)

hello_world("Marvin")
```

フローやタスクを別のモジュールで定義し、それをインポートして使用することもできます。例えば、簡単なサブフローモジュールを以下に示します：

```python
from prefect import flow, task

@flow(name="Subflow")
def my_subflow(msg):
    print(f"Subflow says: {msg}")
```

以下は、`my_subflow()`をインポートしてサブフローとして使用する親フローである：

```python
from prefect import flow, task
from subflow import my_subflow

@task(name="Print Hello")
def print_hello(name):
    msg = f"Hello {name}!"
    print(msg)
    return msg

@flow(name="Hello Flow")
def hello_world(name="world"):
    message = print_hello(name)
    my_subflow(message)

hello_world("Marvin")
```

`hello_world()`フローを実行すると（この例ではhello.pyというファイルから）、次のようなフローランが作成されます：

```
15:19:21.651 | INFO    | prefect.engine - Created flow run 'daft-cougar' for flow 'Hello Flow'
15:19:21.651 | INFO    | Flow run 'daft-cougar' - Using task runner 'ConcurrentTaskRunner'
15:19:21.945 | INFO    | Flow run 'daft-cougar' - Created task run 'Print Hello-84f0fe0e-0' for task 'Print Hello'
Hello Marvin!
15:19:22.055 | INFO    | Task run 'Print Hello-84f0fe0e-0' - Finished in state Completed()
15:19:22.107 | INFO    | Flow run 'daft-cougar' - Created subflow run 'ninja-duck' for flow 'Subflow'
Subflow says: Hello Marvin!
15:19:22.794 | INFO    | Flow run 'ninja-duck' - Finished in state Completed()
15:19:23.215 | INFO    | Flow run 'daft-cougar' - Finished in state Completed('All states completed.')
```

サブフローやタスクは？

Prefectでは、タスクやサブフローを呼び出して、他のタスクの結果をサブフローに渡すなど、ワークフロー内で作業を行うことができます。そこで、よく聞く質問があります：

「タスクではなく、サブフローを使用した方がいい場合とは？」

APIの呼び出し、データベース操作の実行、データポイントの解析や変換など、ワークフロー内で個別の特定の作業を行うタスクを書くことをお勧めします。Prefectタスクは、DaskやRayなどの分散計算フレームワークを使った並列・分散実行に適しています。トラブルシューティングでは、タスクの粒度が高いほど、タスクが失敗したときに問題を発見して修正することが容易になります。

サブフローは、ワークフロー内で関連するタスクをグループ化することができます。ここでは、タスクを個別に呼び出すのではなく、サブフローを使用することを選択する可能性があるシナリオをいくつか紹介します：

- 観察可能性：サブフローは、他のフロー実行と同様に、Prefect UI および Prefect Cloud 内でファーストクラスの観察可能性を持っています。サブフローは、他のフローランと同様に、Prefect UIおよびPrefect Cloudでファーストクラスの観測性を持っています。サブフローの状態は、特定のフローラン内のタスクを掘り下げて見る必要はなく、フローランダッシュボードで確認できます。フロー内のタスクの状態を活用する例については、「最終状態の決定」を参照してください。
- 条件付きフロー： 特定の条件下でのみ実行されるタスクのグループがある場合、それらをサブフロー内にグループ化し、各タスクを個別に実行するのではなく、サブフローを条件付きで実行することができます。
- パラメータ： 異なるユースケースで同じタスク群を実行する場合、実行するサブフローに異なるパラメータを渡すだけで、簡単に実行することができます。
- タスクランナー： サブフローでは、フロー内のタスクに使用するタスクランナーを指定することができます。例えば、Daskで特定のタスクの並列実行を最適化したい場合、Daskタスクランナーを使用するサブフローにタスクをまとめることができます。各サブフローに異なるタスクランナーを使用することも可能です。


## パラメータ

フローは、位置引数とキーワード引数の両方で呼び出すことができます。これらの引数は、実行時に名前と値を対応付けるパラメータの辞書に解決されます。これらのパラメータは、Prefect オーケストレーションエンジンによってフローランオブジェクトに保存されます。

Prefect APIではキーワード引数が必要

Prefect APIからフローランを作成する場合、デフォルトをオーバーライドする際には、パラメータ名を指定する必要があります（位置指定はできません）。

型ヒントは、pydanticを介してフローパラメータに型付けを強制する簡単な方法を提供します。つまり、フロー内で型ヒントとして使用されるpydanticモデルは、自動的に関連するオブジェクトタイプに強制されます：

```python
from prefect import flow
from pydantic import BaseModel

class Model(BaseModel):
    a: int
    b: float
    c: str

@flow
def model_validator(model: Model):
    print(model)
```

パラメータ値は、デプロイメントを使用してAPI経由でフローに提供することができることに注意してください。フロー呼び出し時にAPIに送信されるフロー実行パラメータは、シリアライズ可能なフォームに強制されます。フロー関数の型ヒントは、JSON提供値を適切なPython表現に自動的に強制する方法を提供します。

例えば、何かを自動的にdatetimeに変換する場合です：

```python
from prefect import flow
from datetime import datetime

@flow
def what_day_is_it(date: datetime = None):
    if date is None:
        date = datetime.utcnow()
    print(f"It was {date.strftime('%A')} on {date.isoformat()}")

what_day_is_it("2021-01-01T02:00:19.180906")
# It was Friday on 2021-01-01T02:00:19.180906
```

パラメータは、フローが実行される前に検証されます。フロー呼び出しが無効なパラメーターを受信した場合、フロー実行は`Failed`の状態で作成されます。配備のためのフロー実行が無効なパラメータを受け取った場合、`Running`の状態にならずに`Pending`から`Failed`の状態に移行します。

## 最終的な状態の決定

### 前提条件

このセクションに進む前に、[状態](https://docs.prefect.io/concepts/states)に関するドキュメントを読んでください。

フローの最終状態は、その戻り値によって決定されます。以下のルールが適用されます：

- フロー関数で直接例外が発生した場合、フローランは失敗とマークされます。
- フローが値を返さない（またはNoneを返す）場合、その状態は、フロー内のすべてのタスクとサブフローの状態によって決定される。
- いずれかのタスクの実行やサブフローランが失敗した場合、最終的なフローラン状態は`FAILED`とマークされる。
- タスクの実行がキャンセルされた場合、最終的なフローラン状態は`CANCELLED`としてマークされる。
- フローが手動で作成した状態を返した場合、その状態が最終的なフロー実行の状態として使用されます。これにより、最終状態を手動で決定することができる。
- フロー実行が他のオブジェクトを返す場合、それは完了とマークされる。

以下の例では、これらの各ケースを説明しています：

### 例外の発生

フロー関数内で例外が発生した場合、フローは直ちに失敗とマークされます。

```python
from prefect import flow

@flow
def always_fails_flow():
    raise ValueError("This flow immediately fails")

always_fails_flow()
```

このフローを実行すると、次のような結果になります：

```
22:22:36.864 | INFO    | prefect.engine - Created flow run 'acrid-tuatara' for flow 'always-fails-flow'
22:22:36.864 | INFO    | Flow run 'acrid-tuatara' - Starting 'ConcurrentTaskRunner'; submitted tasks will be run concurrently...
22:22:37.060 | ERROR   | Flow run 'acrid-tuatara' - Encountered exception during execution:
Traceback (most recent call last):...
ValueError: This flow immediately fails
```


### リターンが None の場合

リターンステートメントを持たないフローは、そのすべてのタスクランの状態によって決定されます。

```python
from prefect import flow, task

@task
def always_fails_task():
    raise ValueError("I fail successfully")

@task
def always_succeeds_task():
    print("I'm fail safe!")
    return "success"

@flow
def always_fails_flow():
    always_fails_task.submit().result(raise_on_failure=False)
    always_succeeds_task()

if __name__ == "__main__":
    always_fails_flow()
```

このフローを実行すると、次のような結果が得られます：

```
18:32:05.345 | INFO    | prefect.engine - Created flow run 'auburn-lionfish' for flow 'always-fails-flow'
18:32:05.346 | INFO    | Flow run 'auburn-lionfish' - Starting 'ConcurrentTaskRunner'; submitted tasks will be run concurrently...
18:32:05.582 | INFO    | Flow run 'auburn-lionfish' - Created task run 'always_fails_task-96e4be14-0' for task 'always_fails_task'
18:32:05.582 | INFO    | Flow run 'auburn-lionfish' - Submitted task run 'always_fails_task-96e4be14-0' for execution.
18:32:05.610 | ERROR   | Task run 'always_fails_task-96e4be14-0' - Encountered exception during execution:
Traceback (most recent call last):
  ...
ValueError: I fail successfully
18:32:05.638 | ERROR   | Task run 'always_fails_task-96e4be14-0' - Finished in state Failed('Task run encountered an exception.')
18:32:05.658 | INFO    | Flow run 'auburn-lionfish' - Created task run 'always_succeeds_task-9c27db32-0' for task 'always_succeeds_task'
18:32:05.659 | INFO    | Flow run 'auburn-lionfish' - Executing 'always_succeeds_task-9c27db32-0' immediately...
I'm fail safe!
18:32:05.703 | INFO    | Task run 'always_succeeds_task-9c27db32-0' - Finished in state Completed()
18:32:05.730 | ERROR   | Flow run 'auburn-lionfish' - Finished in state Failed('1/2 states failed.')
Traceback (most recent call last):
  ...
ValueError: I fail successfully
```


futureを返す
フローが1つ以上のfutureを返す場合、最終的な状態は基礎となる状態に基づいて決定されます。

```python
from prefect import flow, task

@task
def always_fails_task():
    raise ValueError("I fail successfully")

@task
def always_succeeds_task():
    print("I'm fail safe!")
    return "success"

@flow
def always_succeeds_flow():
    x = always_fails_task.submit().result(raise_on_failure=False)
    y = always_succeeds_task.submit(wait_for=[x])
    return y

if __name__ == "__main__":
    always_succeeds_flow()
```

このフローを実行すると、次のような結果が得られます。成功したタスクの未来が返されるので、成功したことになります：

```
18:35:24.965 | INFO    | prefect.engine - Created flow run 'whispering-guan' for flow 'always-succeeds-flow'
18:35:24.965 | INFO    | Flow run 'whispering-guan' - Starting 'ConcurrentTaskRunner'; submitted tasks will be run concurrently...
18:35:25.204 | INFO    | Flow run 'whispering-guan' - Created task run 'always_fails_task-96e4be14-0' for task 'always_fails_task'
18:35:25.205 | INFO    | Flow run 'whispering-guan' - Submitted task run 'always_fails_task-96e4be14-0' for execution.
18:35:25.232 | ERROR   | Task run 'always_fails_task-96e4be14-0' - Encountered exception during execution:
Traceback (most recent call last):
  ...
ValueError: I fail successfully
18:35:25.265 | ERROR   | Task run 'always_fails_task-96e4be14-0' - Finished in state Failed('Task run encountered an exception.')
18:35:25.289 | INFO    | Flow run 'whispering-guan' - Created task run 'always_succeeds_task-9c27db32-0' for task 'always_succeeds_task'
18:35:25.289 | INFO    | Flow run 'whispering-guan' - Submitted task run 'always_succeeds_task-9c27db32-0' for execution.
I'm fail safe!
18:35:25.335 | INFO    | Task run 'always_succeeds_task-9c27db32-0' - Finished in state Completed()
18:35:25.362 | INFO    | Flow run 'whispering-guan' - Finished in state Completed('All states completed.')
```


### 複数の状態またはfutureを返す
フローがfutureと状態を混ぜて返す場合、最終的な状態は、すべてのfutureを状態に解決し、状態のいずれかが`COMPLETED`でないかを判断することによって決定されます。

```python
from prefect import task, flow

@task
def always_fails_task():
    raise ValueError("I am bad task")

@task
def always_succeeds_task():
    return "foo"

@flow
def always_succeeds_flow():
    return "bar"

@flow
def always_fails_flow():
    x = always_fails_task()
    y = always_succeeds_task()
    z = always_succeeds_flow()
    return x, y, z
```

このフローを実行すると、次のような結果が得られます。返された3つのフューチャーのうち1つが失敗したため、失敗している。最終的な状態はFailedですが、返された各フューチャーの状態はフローの状態に含まれていることに注意してください：

```
20:57:51.547 | INFO    | prefect.engine - Created flow run 'impartial-gorilla' for flow 'always-fails-flow'
20:57:51.548 | INFO    | Flow run 'impartial-gorilla' - Using task runner 'ConcurrentTaskRunner'
20:57:51.645 | INFO    | Flow run 'impartial-gorilla' - Created task run 'always_fails_task-58ea43a6-0' for task 'always_fails_task'
20:57:51.686 | INFO    | Flow run 'impartial-gorilla' - Created task run 'always_succeeds_task-c9014725-0' for task 'always_succeeds_task'
20:57:51.727 | ERROR   | Task run 'always_fails_task-58ea43a6-0' - Encountered exception during execution:
Traceback (most recent call last):...
ValueError: I am bad task
20:57:51.787 | INFO    | Task run 'always_succeeds_task-c9014725-0' - Finished in state Completed()
20:57:51.808 | INFO    | Flow run 'impartial-gorilla' - Created subflow run 'unbiased-firefly' for flow 'always-succeeds-flow'
20:57:51.884 | ERROR   | Task run 'always_fails_task-58ea43a6-0' - Finished in state Failed('Task run encountered an exception.')
20:57:52.438 | INFO    | Flow run 'unbiased-firefly' - Finished in state Completed()
20:57:52.811 | ERROR   | Flow run 'impartial-gorilla' - Finished in state Failed('1/3 states failed.')
Failed(message='1/3 states failed.', type=FAILED, result=(Failed(message='Task run encountered an exception.', type=FAILED, result=ValueError('I am bad task'), task_run_id=5fd4c697-7c4c-440d-8ebc-dd9c5bbf2245), Completed(message=None, type=COMPLETED, result='foo', task_run_id=df9b6256-f8ac-457c-ba69-0638ac9b9367), Completed(message=None, type=COMPLETED, result='bar', task_run_id=cfdbf4f1-dccd-4816-8d0f-128750017d0c)), flow_run_id=6d2ec094-001a-4cb0-a24e-d2051db6318d)
```


#### 複数の状態を返す

複数の状態を返す場合、それらはセット、リスト、タプルのいずれかに含まれなければならない。他のコレクションタイプを使用する場合、含まれる状態の結果はチェックされません。

### 手動で作成した状態を返す

フローが手動で作成した状態を返す場合、戻り値に基づいて最終的な状態が決定されます。

```python
from prefect import task, flow
from prefect.server.schemas.states import Completed, Failed

@task
def always_fails_task():
    raise ValueError("I fail successfully")

@task
def always_succeeds_task():
    print("I'm fail safe!")
    return "success"

@flow
def always_succeeds_flow():
    x = always_fails_task.submit()
    y = always_succeeds_task.submit()
    if y.result() == "success":
        return Completed(message="I am happy with this result")
    else:
        return Failed(message="How did this happen!?")

if __name__ == "__main__":
    always_succeeds_flow()
```

このフローを実行すると、次のような結果が得られます。

```
18:37:42.844 | INFO    | prefect.engine - Created flow run 'lavender-elk' for flow 'always-succeeds-flow'
18:37:42.845 | INFO    | Flow run 'lavender-elk' - Starting 'ConcurrentTaskRunner'; submitted tasks will be run concurrently...
18:37:43.125 | INFO    | Flow run 'lavender-elk' - Created task run 'always_fails_task-96e4be14-0' for task 'always_fails_task'
18:37:43.126 | INFO    | Flow run 'lavender-elk' - Submitted task run 'always_fails_task-96e4be14-0' for execution.
18:37:43.162 | INFO    | Flow run 'lavender-elk' - Created task run 'always_succeeds_task-9c27db32-0' for task 'always_succeeds_task'
18:37:43.163 | INFO    | Flow run 'lavender-elk' - Submitted task run 'always_succeeds_task-9c27db32-0' for execution.
18:37:43.175 | ERROR   | Task run 'always_fails_task-96e4be14-0' - Encountered exception during execution:
Traceback (most recent call last):
  ...
ValueError: I fail successfully
I'm fail safe!
18:37:43.217 | ERROR   | Task run 'always_fails_task-96e4be14-0' - Finished in state Failed('Task run encountered an exception.')
18:37:43.236 | INFO    | Task run 'always_succeeds_task-9c27db32-0' - Finished in state Completed()
18:37:43.264 | INFO    | Flow run 'lavender-elk' - Finished in state Completed('I am happy with this result')
```


### オブジェクトを返す

フローランが他のオブジェクトを返した場合、完了と表示されます。

```python
from prefect import task, flow

@task
def always_fails_task():
    raise ValueError("I fail successfully")

@flow
def always_succeeds_flow():
    always_fails_task().submit()
    return "foo"

if __name__ == "__main__":
    always_succeeds_flow()
```

このフローを実行すると、次のような結果になります。

```
21:02:45.715 | INFO    | prefect.engine - Created flow run 'sparkling-pony' for flow 'always-succeeds-flow'
21:02:45.715 | INFO    | Flow run 'sparkling-pony' - Using task runner 'ConcurrentTaskRunner'
21:02:45.816 | INFO    | Flow run 'sparkling-pony' - Created task run 'always_fails_task-58ea43a6-0' for task 'always_fails_task'
21:02:45.853 | ERROR   | Task run 'always_fails_task-58ea43a6-0' - Encountered exception during execution:
Traceback (most recent call last):...
ValueError: I am bad task
21:02:45.879 | ERROR   | Task run 'always_fails_task-58ea43a6-0' - Finished in state Failed('Task run encountered an exception.')
21:02:46.593 | INFO    | Flow run 'sparkling-pony' - Finished in state Completed()
Completed(message=None, type=COMPLETED, result='foo', flow_run_id=7240e6f5-f0a8-4e00-9440-a7b33fb51153)
```

## フローランを一時停止する

Prefectは、手動承認のために進行中のフローランを一時停止することができます。  
Prefectは、`pause_flow_run`関数と`resume_flow_run`関数、およびPrefectサーバーやPrefect Cloud UIを介してこの機能を公開します。

最も簡単なのは、フロー内部で `pause_flow_run` を呼び出すことです。タイムアウトオプションも指定でき、指定した秒数後にフローが再開されないと失敗します。

```python
from prefect import task, flow, pause_flow_run, resume_flow_run

@task
async def marvin_setup():
    return "a raft of ducks walk into a bar..."
@task
async def marvin_punchline():
    return "it's a wonder none of them ducked!"
@flow
async def inspiring_joke():
    await marvin_setup()
    await pause_flow_run(timeout=600)  # pauses for 10 minutes
    await marvin_punchline()
```

このフローを呼び出すと、最初のタスクの後に一時停止し、再開を待ちます。

```
await inspiring_joke()
> "a raft of ducks walk into a bar..."
```

一時停止したフロー実行は、Prefect UIのResumeボタンをクリックするか、クライアントのコードにより`resume_flow_run`ユーティリティを呼び出すことで再開することができます。

```python
resume_flow_run(FLOW_RUN_ID)
```

一時停止していたフローランは、その後終了します！

```
> "it's a wonder none of them ducked!"
```

一時停止中のフロー実行をブロックしないフローの例を示します。このフローは、1つのタスクの後に終了し、再開時に再スケジュールされます。最初のタスクの保存された結果は、再実行されるのではなく、取得されます。

```python
from prefect import flow, pause_flow_run, task

@task(persist_result=True)
def foo():
    return 42

@flow(persist_result=True)
def noblock_pausing():
    x = foo.submit()
    pause_flow_run(timeout=30, reschedule=True)
    y = foo.submit()
    z = foo(wait_for=[x])
    alpha = foo(wait_for=[y])
    omega = foo(wait_for=[x, y])
```

この長時間流れるフローは、`pause_flow_run(flow_run_id=<ID>)`を呼び出すか、Prefect UIまたはPrefect CloudでPauseボタンを選択することにより、プロセス外で一時停止できます。

```python
from prefect import flow, task
import time

@task(persist_result=True)
async def foo():
    return 42

@flow(persist_result=True)
async def longrunning():
    res = 0
    for ii in range(20):
        time.sleep(5)
        res += (await foo())
    return res
```

フローランの一時停止はデフォルトでブロックされる

デフォルトでは、フロー実行の一時停止はエージェントをブロックします - フローは`pause_flow_run`関数内でまだ実行中です。しかし、この方法で、非展開ローカルフロー実行とサブフローを含む、任意のフロー実行を一時停止することができます。

あるいは、フロー実行プロセスをブロックすることなく、フロー実行を一時停止することができます。これは、エージェント経由でフローを実行し、一時停止したフローが一時停止している間にエージェントが他のフローをピックアップできるようにしたい場合に特に有用です。

ノンブロッキングの一時停止は、`reschedule`フラグを`True`に設定することで実現可能です。この機能を使用するためには、`reschedule`フラグで一時停止するフローは、以下を備えている必要があります：

- 関連するデプロイメント
- `persist_results` フラグで設定された結果

## フローランをキャンセル

CLI、UI、REST API、またはPythonクライアントから、スケジュール済みまたは進行中のフロー実行をキャンセルすることができます。

キャンセルが要求されると、フローランは「Cancelling」状態に移行します。エージェントはフローランの状態を監視し、キャンセルが要求されたことを検出します。その後、エージェントはフローランのインフラストラクチャに信号を送信し、ランの終了を要求します。猶予期間（デフォルトは30秒）が経過してもランが終了しない場合、インフラストラクチャは強制終了され、フローランが終了することが保証されます。

エージェントが必要です

フローランのキャンセルには、エージェントによってフローランが提出され、キャンセルを実施するためのエージェントが実行されていることが必要です。デプロイメントされていないフローランは、まだキャンセルできません。

キャンセルのサポートは、すべてのコアライブラリのインフラストラクチャタイプに含まれています：

- Dockerコンテナ
- Kubernetesジョブ
- プロセス

キャンセルは、エージェントの再起動に対して堅牢です。これを可能にするために、作成されたインフラストラクチャに関するメタデータをフロー実行に添付します。内部では、これを`infrastructure_pid`またはinfrastructure identifierと呼びます。一般的に、これは2つの部分から構成されます：

1. Scope：インフラストラクチャが実行されている場所を特定します。
2. ID：スコープ内のインフラストラクチャの一意な識別子。

Scopeは、Prefect が間違ったインフラストラクチャを kill しないようにするために使用されます。たとえば、複数のマシンで実行されているエージェントは、プロセスIDが重複していても、スコープが一致しないはずです。

主なインフラストラクチャの種類の識別子は、次のとおりです：

- プロセス：マシンのホスト名とPID。
- Dockerコンテナ： Docker Containers: Docker API URLとコンテナID。
- Kubernetesジョブ： Kubernetesのクラスタ名とジョブ名。

キャンセルプロセスは堅牢ですが、いくつかの問題が発生する可能性があります：

- フローランのインフラストラクチャーブロックが削除または変更されている場合、キャンセルが機能しないことがあります。
- フローランのインフラストラクチャーブロックが削除または変更された場合、キャンセルは機能しない可能性があります。
- フローランをキャンセルしようとしたときに、識別子のスコープが一致しない場合、エージェントはフローランをキャンセルすることができない。別のエージェントがキャンセルを試みることができる。
- ランに関連するインフラストラクチャが見つからないか、すでに強制終了されている場合、エージェントはフローランをキャンセルとしてマークします。
- `infrastructre_pid`がフローランから欠落している場合、キャンセルされたとマークされますが、キャンセルを強制することはできません。
- エージェントがキャンセル中に予期せぬエラーに遭遇した場合、エラーが発生した場所によって、フローランはキャンセルされる場合とされない場合があります。エージェントは、フローランのキャンセルを再度試みます。別のエージェントがキャンセルを試みることもあります。

### CLIでキャンセル

実行環境のコマンドラインから、`prefect flow-run cancel` CLIコマンドを使用し、フローランのIDを渡してフローランをキャンセルすることができます。

```
$ prefect flow-run cancel 'a55a4804-9e3c-4042-8b59-b3b6b7618736' です。
```

### UIからキャンセル

UI からは、フローランの詳細ページに移動し、右上の Cancel ボタンをクリックすることで、フローランをキャンセルすることができます。

![Prefect UI](https://docs.prefect.io/latest/img/ui/flow-run-cancellation-ui.png)

## 状態フックを設定

フローランが特定の状態（`Failed`など）になったときにクライアントサイドフックを実行するために、状態フックを設定することができます：

例えば、フローランが失敗したときにSlackに通知を送るには、on_failureフックを使用します：

```python
from prefect import flow
from prefect.blocks.core import Block
from prefect.settings import PREFECT_API_URL

def notify_slack(flow, flow_run, state):
    slack_webhook_block = Block.load("slack-webhook/my-slack-webhook")

    slack_webhook_block.notify(
        f"Your job {flow_run.name} entered {state.name} with message:\n\n>{state.message}\n\n"
        f"See <https://{PREFECT_API_URL.value()}/flow-runs/flow-run/{flow_run.id}|the flow run in the UI>\n\n"
        f"Tags: {flow_run.tags}\n\n"
        f"Scheduled start time = {flow_run.expected_start_time}\n"
    )

@flow(on_failure=[notify_slack], retries=1)
def noisy_flow():
    raise ValueError("oops!")

if __name__ == "__main__":
    noisy_flow()
```

`on_failure`フックは、すべての再試行が完了し、フローランが最終的に`Failed`状態になるまで実行されないことに注意してください。