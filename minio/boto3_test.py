# モジュールディレクトリ指定
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'py-pkgs'))

import boto3

if __name__ == '__main__':
    s3 = boto3.resource(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='admin', # ログイン名
        aws_secret_access_key='adminpass', # ログインパスワード
    )

    # MinIOのバケット出力
    print('バケット一覧')
    for bucket in s3.buckets.all():
        print(bucket.name)
    print('')

    # MinIO内のfirst.csvの中身出力
    print('first.csvの中身')
    obj = s3.Object('sample','first.csv')
    res = obj.get()
    print(res['Body'].read().decode())
