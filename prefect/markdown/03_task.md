# タスク（task）

タスクは、Prefect のワークフローにおける個別の作業単位を表す関数です。  
タスクは必須ではありません。  
通常の Python ステートメントと関数を使用して、フローのみで構成される Prefect ワークフローを定義することができます。  

タスクは、ワークフローロジックの要素を観察可能な単位でカプセル化し、フローやサブフロー間で再利用することができます。

## タスクの概要

タスクは関数であり、入力を受け取り、作業を実行し、出力を返すことができます。Prefectのタスクは、Pythonの関数ができることはほとんどすべてできます。

タスクは、実行前に上流の依存関係や依存関係の状態に関するメタデータを受け取るので、たとえ依存関係から明示的なデータ入力を受けなくても、特別なタスクになります。これにより、例えば、タスクが実行する前に他のタスクの完了を待つようにすることができます。

また、タスクは、Prefectの自動ロギングを利用して、実行時間、タグ、最終状態などのタスク実行に関する詳細を記録します。

タスクは、フロー定義と同じファイル内で定義することも、モジュール内でタスクを定義し、フロー定義で使用するためにインポートすることも可能です。すべてのタスクは、フロー内から呼び出す必要があります。タスクは、他のタスクから呼び出すことはできません。

### フローからタスクを呼び出す

関数をタスクとして指定するには、`@task`デコレータを使用します。フロー関数内からタスクを呼び出すと、新しいタスクランが作成されます：

```python
from prefect import flow, task

@task
def my_task():
    print("Hello, I'm a task")

@flow
def my_flow():
    my_task()
```

タスクは、タスク名、関数の完全修飾名、およびタグからなるハッシュであるタスクキーによって一意に識別される。タスクに名前が指定されていない場合、名前はタスク関数から派生します。

タスクの大きさはどのくらいがいいのでしょうか？

Prefectでは、ワークフローの1つの論理的なステップを表す「小さなタスク」を推奨しています。これにより、Prefect は、タスクの失敗をより適切に抑制することができます。

はっきり言って、すべてのコードを1つのタスクに入れることを妨げるものは何もありません - Prefectは喜んでそれを実行します！しかし、コードの1行でも失敗すると、タスク全体が失敗し、最初からやり直さなければなりません。これは、コードを複数の依存タスクに分割することで回避できます。

タスクの関数を他のタスクから呼び出す

Prefectでは、他のタスクからタスクの実行をトリガーすることはできません。タスクの関数を直接呼び出したい場合は、`task.fn()`を使用します。

```python
from prefect import flow, task

@task
def my_first_task(msg):
    print(f"Hello, {msg}")

@task
def my_second_task(msg):
    my_first_task.fn(msg)

@flow
def my_flow():
    my_second_task("Trillian")
```

上記の例では、実際にタスクの実行を発生させることなく、タスクの関数を呼び出しているだけであることに注意してください。この方法でタスクの関数を呼び出すと、PrefectはPrefectのバックエンドでタスクの実行を追跡しません。また、この関数呼び出しでは、リトライなどの機能を使用することができません。

## タスクの引数

タスクは、引数によって多くのカスタマイズが可能です。例えば、リトライの動作、名前、タグ、キャッシングなどです。タスクには、以下のオプション引数があります。

|引数 |説明 |
|- |- |
|`name` |タスクの名前（オプション）です。提供されない場合、名前は関数名から推論されます。
|`description` |タスクの説明（文字列）を指定します。提供されない場合、説明は、装飾された関数のdocstringから引き出されます。
|`tags` |タスクの実行に関連付けられるタグのオプションのセット。これらのタグは、タスクの実行時に prefect.tags コンテキストで定義されているタグと組み合わせられます。
|`cache_key_fn` |タスクの実行コンテキストと呼び出しパラメーターが与えられると、文字列キーが生成されるオプションのコール可能です。キーが以前の完了した状態に一致する場合、タスクを再度実行する代わりにその状態結果が復元されます。
|`cache_expiration` |このタスクのキャッシュされた状態が復元可能である期間を示すオプションの時間量。
|`task_run_name` |この名前は、タスクのキーワード引数を変数とする文字列テンプレートとして提供することができる。この名前は、文字列を返す関数を介して提供することもできる。
|`retries` |タスクの実行に失敗した場合に再試行する回数（オプション）。
|`retry_delay_seconds` |失敗したタスクの再試行前に待つ秒数（オプション）。`retries`が0でない場合のみ適用される。|
|`version` |このタスク定義のバージョンを指定するオプションの文字列。|

例えば、タスクの`name`の値を指定することができます。ここでは、オプションのdescription引数も使用しています。

```python
@task(name="hello-task", 
      description="This task says hello.")
def my_task():
    print("Hello, I'm a task")
```

この設定では、タスクのキーワード引数へのテンプレート化された参照をオプションで含むことができる文字列を受け付け、このタスクの実行を区別することができます。この設定は、オプションでタスクのキーワード引数へのテンプレート参照を含むことができる文字列を受け入れます。この名前は、ここで見られるように、Pythonの標準的な文字列書式構文を使ってフォーマットされます：

```python
import datetime
from prefect import flow, task

@task(name="My Example Task", 
      description="An example task for a tutorial.",
      task_run_name="hello-{name}-on-{date:%A}")
def my_task(name, date):
    pass

@flow
def my_flow():
    # creates a run with a name like "hello-marvin-on-Thursday"
    my_task(name="marvin", date=datetime.datetime.utcnow())
```

さらに、この設定には、タスクの実行名に使用する文字列を返す関数も使用できます：

```python
import datetime
from prefect import flow, task

def generate_task_name():
    date = datetime.datetime.utcnow()
    return f"{date:%A}-is-a-lovely-day"

@task(name="My Example Task",
      description="An example task for a tutorial.",
      task_run_name=generate_task_name)
def my_task(name):
    pass

@flow
def my_flow():
    # creates a run with a name like "Thursday-is-a-lovely-day"
    my_task(name="marvin")
```

タスクに関する情報へのアクセスが必要な場合は、`prefect.runtime`モジュールを使用します。例えば、以下のようになります：

```python
from prefect import flow
from prefect.runtime import flow_run, task_run

def generate_task_name():
    flow_name = flow_run.flow_name
    task_name = task_run.task_name

    parameters = task_run.parameters
    name = parameters["name"]
    limit = parameters["limit"]

    return f"{flow_name}-{task_name}-with-{name}-and-{limit}"

@task(name="my-example-task",
      description="An example task for a tutorial.",
      task_run_name=generate_task_name)
def my_task(name: str, limit: int = 100):
    pass

@flow
def my_flow(name: str):
    # creates a run with a name like "my-flow-my-example-task-with-marvin-and-100"
    my_task(name="marvin")
```

## タグ

タグは、オプションの文字列ラベルで、名前やフロー以外のタスクを識別し、グループ化することができます。タグは以下のような用途に使用できます：

- UI および [Prefect REST API](https://docs.prefect.io/api-ref/rest-api/#filtering) で、タグによってタスクの実行をフィルタリングする。
- タグによるタスク実行の並行性制限を設定する。

タグは、タスクデコレータのキーワード引数として指定することができます。

```python
@task(name="hello-task", tags=["test"])
def my_task():
    print("Hello, I'm a task")
```

また、タグコンテキストマネージャーでタグを引数として与え、タスクの定義ではなく、タスクが呼び出されたときにタグを指定することができます。

```python
from prefect import flow, task
from prefect import tags

@task
def my_task():
    print("Hello, I'm a task")

@flow
def my_flow():
    with tags("test"):
        my_task()
```

## リトライについて

Prefectのタスクは、失敗したときに自動的にリトライすることができます。リトライを有効にするには、`retries`と`retry_delay_seconds`パラメータをタスクに渡します。このタスクは最大3回までリトライを行い、各リトライの間に60秒の待ち時間が発生します：

```python
import requests
from prefect import task, flow

@task(retries=3, retry_delay_seconds=60)
def get_page(url):
    page = requests.get(url)
```

タスクのリトライを設定する際、各リトライに特定の遅延時間を設定することができます。`retry_delay_seconds`オプションは、カスタムリトライ動作のための遅延のリストを受け付けます。次のタスクは、次の試行を開始する前に、それぞれ1秒、10秒、100秒の連続的に増加する間隔を待ちます：

```python
from prefect import task, flow

@task(retries=3, retry_delay_seconds=[1, 10, 100])
```

さらに、リトライ回数を引数として受け取り、リストを返すcallableを渡すことができます。Prefectには、指数関数的バックオフ再試行戦略に対応する再試行遅延のリストを自動生成するexponential_backoffユーティリティが含まれています。次のフローは、各リトライの前に10秒、20秒、40秒の順に待機します。

```python
from prefect import task, flow
from prefect.tasks import exponential_backoff

@task(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=10))
```

指数関数的バックオフを使用する場合、多くのタスクが全く同時に再試行し、カスケード障害を引き起こす「Thundering Herd」シナリオを防ぐために、遅延時間をジッター化したい場合もあります。  
`retry_jitter_factor`オプションを使用すると、基本遅延に分散を加えることができます。例えば、10秒のリトライ遅延にretry_jitter_factorを0.5とすると、最大15秒の遅延が許容されます。  `retry_jitter_factor`の値が大きいと、平均再試行遅延時間を一定に保ちつつ、「雷の群れ」に対する保護が強化されます。
たとえば、次のタスクでは、指数関数的バックオフにジッターを追加しているため、リトライ遅延はそれぞれ最大遅延時間20秒、40秒、80秒まで変化します。

```python
from prefect import task, flow
from prefect.tasks import exponential_backoff

@task(
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=10),
    retry_jitter_factor=1,
)
```

また、以下のグローバル設定を使用して、再試行と再試行遅延を設定することができます。これらの設定は、フローまたはタスクデコレータで設定されたretryまたはretry_delay_secondsを上書きするものではありません。

```
prefect config set PREFECT_FLOW_DEFAULT_RETRIES=2
prefect config set PREFECT_TASK_DEFAULT_RETRIES=2
prefect config set PREFECT_FLOW_DEFAULT_RETRY_DELAY_SECONDS = [1, 10, 100]
prefect config set PREFECT_TASK_DEFAULT_RETRY_DELAY_SECONDS = [1, 10, 100]
```

再試行で新しいタスクランが作成されない

タスクがリトライされても、新しいタスクランは作成されません。新しい状態は、元のタスク実行の状態履歴に追加されます。

## キャッシング

キャッシングとは、タスクを定義するコードを実際に実行することなく、タスク実行の終了状態を反映させる機能のことです。これにより、フロー実行のたびに実行するのはコストがかかるタスクの結果を効率的に再利用したり、タスクへの入力が変更されていない場合にキャッシュされた結果を再利用したりすることができます。

タスクの実行時にキャッシュされた状態を取得すべきかどうかを判断するために、「キャッシュ・キー」を使用します。キャッシュ・キーは、ある実行を他の実行と同一とみなすかどうかを示す文字列値である。キャッシュ・キーが設定されたタスク実行が終了すると、そのキャッシュ・キーがステートに付加されます。各タスクランの開始時に、Prefectは、一致するキャッシュキーを持つステートをチェックします。同一のキーを持つステートが見つかった場合、Prefectはタスクを再度実行する代わりに、キャッシュされたステートを使用します。

キャッシュを有効にするには、タスクに `cache_key_fn` （キャッシュ・キーを返す関数）を指定します。オプションで、キャッシュの有効期限を示す `cache_expiration` timedelta を指定することができます。`cache_expiration`を指定しない場合、キャッシュ・キーは期限切れになりません。

Prefect `task_input_hash` を使用すると、入力に基づきキャッシュされるタスクを定義することができます。これは、JSONまたはcloudpickleシリアライザーを使用してタスクへのすべての入力をハッシュ化するタスクキャッシュキーの実装です。タスクの入力が変化しない場合、キャッシュが切れるまでタスクを実行するのではなく、キャッシュされた結果が使用されます。

引数がJSONシリアライズ可能でない場合、pickleシリアライザーがフォールバックとして使用されることに注意してください。cloudpickleが失敗した場合、`task_input_hash`は与えられた入力に対してキャッシュキーが生成できなかったことを示す`null`キーを返します。

この例では、`cache_expiration` timeが終了するまで、`hello_task()`が呼び出されたときに入力が同じである限り、キャッシュされた戻り値が返される。この状態では、タスクは再実行されない。しかし、入力引数の値が変化した場合、`hello_task()`は新しい入力を使って実行される。

```python
from datetime import timedelta
from prefect import flow, task
from prefect.tasks import task_input_hash

@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def hello_task(name_input):
    # Doing some work
    print("Saying hello")
    return "hello " + name_input

@flow
def hello_flow(name_input):
    hello_task(name_input)
```

また、文字列のキャッシュ・キーを返す独自の関数やその他の呼び出し可能なものを提供することもできます。一般的な `cache_key_fn` は、2 つの位置引数を受け付ける関数です：

- 第1引数は`TaskRunContext`に対応し、タスク実行メタデータを`task_run_id`、`flow_run_id`、`task`という属性に格納します。
- 第2引数は、タスクへの入力値の辞書に対応する。例えば、タスクが`fn(x, y, z)`というシグネチャーで定義されている場合、辞書にはキャッシュキーの計算に使用できる対応する値を持つ `"x"`, `"y"`, `"z"` というキーが含まれます。

`cache_key_fn`は`@task`として定義されていないことに注意してください。

タスクキャッシュキー

デフォルトでは、タスクキャッシュキーは2000文字に制限されており、`PREFECT_API_TASK_CACHE_KEY_MAX_LENGTH`設定によって指定されます。

```python
from prefect import task, flow

def static_cache_key(context, parameters):
    # return a constant
    return "static cache key"

@task(cache_key_fn=static_cache_key)
def cached_task():
    print('running an expensive operation')
    return 42

@flow
def test_caching():
    cached_task()
    cached_task()
    cached_task()
```

この場合、キャッシュキーの有効期限もなく、キャッシュキーを変更するロジックもないので、`cached_task()`は1回だけ実行されます。

```
>>> test_caching()
running an expensive operation
>>> test_caching()
>>> test_caching()
```

各タスクが Running 状態になるよう要求されたとき、`cache_key_fn` から計算されたキャッシュ・キーを提供しました。Prefectバックエンドは、このキーに関連する`COMPLETED`状態があることを特定し、同じ戻り値を含む同じ`COMPLETED`状態に直ちに入るようランに指示します。

実際の例では、同じフローランで繰り返される呼び出しのみがキャッシュされるように、キャッシュキーにコンテキストからフローランIDを含めることができる。

```python
def cache_within_flow_run(context, parameters):
    return f"{context.task_run.flow_run_id}-{task_input_hash(context, parameters)}"

@task(cache_key_fn=cache_within_flow_run)
def cached_task():
    print('running an expensive operation')
    return 42
```

タスクの結果、リトライ、キャッシング

タスク結果は、フロー実行中にメモリにキャッシュされ、`PREFECT_LOCAL_STORAGE_PATH`設定によって指定された場所に永続化されます。その結果、フロー実行間のタスクキャッシュは、現在、そのローカルストレージパスにアクセスできるフロー実行に限定されています。

### キャッシュのリフレッシュ

タスクがキャッシュを使用する代わりに、そのキャッシュ・キーに関連するデータを更新したい場合があります。これはキャッシュの "リフレッシュ "である。

`refresh_cache`オプションを使用すると、特定のタスクに対してこの動作を有効にすることができます：

```python
import random

def static_cache_key(context, parameters):
    # return a constant
    return "static cache key"

@task(cache_key_fn=static_cache_key, refresh_cache=True)
def caching_task():
    return random.random()
```

このタスクが実行されると、キャッシュされた値を使うのではなく、常にキャッシュキーを更新するようになります。これは、キャッシュの更新を担当するフローがある場合に特に便利です。

すべてのタスクでキャッシュを更新したい場合は、`PREFECT_TASKS_REFRESH_CACHE`設定を使用することができます。`PREFECT_TASKS_REFRESH_CACHE=true`を設定すると、すべてのタスクのデフォルト動作がリフレッシュされるように変更されます。これは、キャッシュされた結果なしでフローを再実行したい場合に特に便利です。

この設定を有効にしてもリフレッシュしないタスクがある場合は、明示的に`refresh_cache`を`False`に設定することができます。これらのタスクはキャッシュを更新しません。キャッシュ・キーが存在する場合は、更新されずに読み込まれます。キャッシュ・キーがまだ存在しない場合、これらのタスクはまだキャッシュに書き込むことができることに注意してください。

```python
@task(cache_key_fn=static_cache_key, refresh_cache=False)
def caching_task():
    return random.random()
```


## タイムアウト

タスクのタイムアウトは、意図しないタスクの長時間実行を防ぐために使用されます。タスクの実行時間がタイムアウトで指定した時間を超えると、タイムアウト例外が発生し、そのタスクは失敗とマークされます。UIでは、タスクは`TimedOut`として目に見える形で指定されます。フローの観点からは、タイムアウトしたタスクは、他の失敗したタスクと同様に扱われます。

タイムアウトの期間は、`timeout_seconds`キーワード引数を使用して指定します。

```python
from prefect import task, get_run_logger
import time

@task(timeout_seconds=1)
def show_timeouts():
    logger = get_run_logger()
    logger.info("I will execute")
    time.sleep(5)
    logger.info("I will not execute")
```

## タスクの結果

タスクの呼び出し方によって、タスクは異なるタイプの結果を返し、オプションでタスクランナーを使用することができます。

どのようなタスクでも、次のような結果を返すことができます：

- データ（`int`、`str`、`dict`、`list`など） - これは、`your_task()`を呼び出したときのデフォルトの動作です。
- `PrefectFuture` - これは`your_task.submit()` を呼び出すことで実現されます。`PrefectFuture` には、データと State が含まれます。
- Prefect `State` - 引数 `return_state=True` でタスクまたはフローを呼び出すと、タスクまたはフローの失敗や再試行など、気になる状態変化に基づいてカスタム動作を構築するために使用できる状態を直接返します。

タスクランナーでタスクを実行するには、`.submit()`でタスクを呼び出す必要があります。

例として、状態の戻り値を参照してください。

タスクランナーはオプションです

タスクの結果が必要なだけなら、フローからタスクを呼び出すだけでよい。ほとんどのワークフローでは、タスクを直接呼び出して結果を受け取るというデフォルトの動作が、必要なものすべてです。


## 待機

データを交換しないが、一方が他方の終了を待つ必要がある2つのタスクの間に依存関係を作成するには、特別な`wait_for`キーワード引数を使用します：

```python
@task
def task_1():
    pass

@task
def task_2():
    pass

@flow
def my_flow():
    x = task_1()

    # task 2 will wait for task_1 to complete
    y = task_2(wait_for=[x])
```

## マップ

Prefectは、入力データの各要素に対して自動的にタスクランを作成する`.map()`実装を提供します。  
マップされたタスクは、多くの個々の子タスクの計算を表します。

Prefectの最も単純なマップは、タスクを受け取り、その入力の各要素に適用します。

```python
from prefect import flow, task

@task
def print_nums(nums):
    for n in nums:
        print(n)

@task
def square_num(num):
    return num**2

@flow
def map_flow(nums):
    print_nums(nums)
    squared_nums = square_num.map(nums) 
    print_nums(squared_nums)

map_flow([1, 2, 3, 5, 8, 13])
```

Prefectはマッピングされない引数もサポートしており、マッピングされない静的な値を渡すことができます。

```python
from prefect import flow, task

@task
def add_together(x, y):
    return x + y

@flow
def sum_it(numbers, static_value):
    futures = add_together.map(numbers, static_value)
    return futures

sum_it([1, 2, 3], 5)
```

static引数がiterableの場合は、`unmapped`でラップして、Prefectにstatic valueとして扱うことを伝える必要があります。

```python
from prefect import flow, task, unmapped

@task
def sum_plus(x, static_iterable):
    return x + sum(static_iterable)

@flow
def sum_it(numbers, static_iterable):
    futures = sum_plus.map(numbers, static_iterable)
    return futures

sum_it([4, 5, 6], unmapped([1, 2, 3]))
```

## 非同期タスク

Prefectは、デフォルトで非同期タスクとフロー定義もサポートしています。非同期の標準的なルールはすべて適用されます：

```python
import asyncio

from prefect import task, flow

@task
async def print_values(values):
    for value in values:
        await asyncio.sleep(1) # yield
        print(value, end=" ")

@flow
async def async_flow():
    await print_values([1, 2])  # runs immediately
    coros = [print_values("abcd"), print_values("6789")]

    # asynchronously gather the tasks
    await asyncio.gather(*coros)

asyncio.run(async_flow())
```

なお、`asyncio.gather`を使用しない場合、`ConcurrentTaskRunner`で非同期実行するためには、`.submit()`を呼び出す必要がある。

## タスク実行の並行性制限

同時に実行されるタスクの数が多すぎることを積極的に防ぎたい状況があります。例えば、複数のフローにまたがる多くのタスクが、10個の接続しか許可されていないデータベースと対話するように設計されている場合、このデータベースに接続するタスクが常に10個以上実行されていないことを確認したい。

Prefectには、これを実現するための機能として、タスクの同時実行数制限が組み込まれています。

タスクの同時実行数制限は、タスク・タグを使用します。オプションの同時実行数制限は、指定されたタグを持つタスクの `Running` 状態での同時実行の最大数として指定できます。指定された同時実行制限は、そのタグが適用されたすべてのタスクに適用されます。

タスクが複数のタグを持つ場合、すべてのタグが利用可能な同時実行数を持つ場合にのみ実行されます。

明示的な制限のないタグは、無制限の同時実行が可能であるとみなされます。

同時実行数制限0はタスクの実行を中止する

現在、タグの同時実行数制限を0に設定した場合、そのタグでタスクを実行しようとすると、遅延ではなく、中止されます。

### 実行時の動作

タスクタグの制限は、タスク実行が実行状態に入ろうとするたびにチェックされます。

タスクのタグに利用可能な同時実行スロットがない場合、実行状態への移行は遅延され、30秒後に実行状態への移行を再度試みるようクライアントに指示されます。

サブフローでの同時実行数制限

サブフローでのタスク実行に同時実行数制限をかけると、デッドロックが発生することがあります。ベストプラクティスとして、サブフローでのタスク実行に制限を設けないように、タグと同時実行制限を設定してください。

### 同時実行数制限の設定

フロー実行の同時実行数制限は、ワークプールやワークキューレベルで設定されます。

タスクランの同時実行制限はタグで設定されますが（下図）、フローランの同時実行制限はワークプールやワークキューで設定されます。

タグの数だけ同時実行の制限を設定することができます。制限を設定できるのは

- Prefect CLI
- `PrefectClient` Pythonクライアントを使用したPrefect API
- PrefectサーバーUIまたはPrefectクラウド

#### CLIの場合

Prefect CLI の `concurrency-limit` コマンドを使用すると、同時実行の制限を作成、リスト、および削除することができます。

```
$ prefect concurrency-limit [command] [arguments]
```

|コマンド |説明|
|- |- |
|`create` |タグと制限を指定して、同時実行制限を作成します。|
|`delete` |指定したタグに設定されている同時実行制限を削除します。|
|`inspect` |指定されたタグに設定された同時実行制限の詳細を表示します。|
|`ls` |定義されたすべての同時実行制限を表示します。|

例えば、`small_instance`タグに同時実行制限を10に設定するには、次のようにします：

```
$ prefect concurrency-limit create small_instance 10
```

`small_instance`タグの同時実行制限を削除するには、次のようにします：

```
$ prefect concurrency-limit delete small_instance
```

`small_instance` タグの同時実行数制限の詳細を表示するには、次のようにします：

```
$ prefect concurrency-limit inspect small_instance
```

#### Pythonクライアント

タグの同時実行制限をプログラムで更新するには、`PrefectClient.orchestration.create_concurrency_limit`を使用します。

`create_concurrency_limit`は、2つの引数を取ります：

- `tag` は、制限を設定するタスクタグを指定します。
- `concurrency_limit`は、そのタグの同時実行タスクの最大数を指定します。

例えば、`small_instance`タグに同時実行の上限を10に設定するには、次のようにします：

```python
from prefect.client import get_client

async with get_client() as client:
    # set a concurrency limit of 10 on the 'small_instance' tag
    limit_id = await client.create_concurrency_limit(
        tag="small_instance", 
        concurrency_limit=10
        )
```

タグのすべての同時実行制限を削除するには、タグを渡して`PrefectClient.delete_concurrency_limit_by_tag`を使用します：

```python
async with get_client() as client:
    # remove a concurrency limit on the 'small_instance' tag
    await client.delete_concurrency_limit_by_tag(tag="small_instance")
```

タグに設定されている制限値を照会したい場合は、`PrefectClient.read_concurrency_limit_by_tag`でタグを指定して照会します：

すべてのタグに設定されている制限値を確認するには、`PrefectClient.read_concurrency_limits`を使用します。

```python
async with get_client() as client:
    # query the concurrency limit on the 'small_instance' tag
    limit = await client.read_concurrency_limit_by_tag(tag="small_instance")
```
