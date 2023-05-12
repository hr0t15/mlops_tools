#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import json
import tempfile
import pathlib

import mlflow
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_validate


def main():
    # データセットの読み込み
    dataset = datasets.load_breast_cancer()
    X, y = dataset.data, dataset.target
    feature_names = dataset.feature_names

    # 5-Fold Stratified CV でスコアを確認する
    clf = RandomForestClassifier(n_estimators=100,
                                 random_state=42,
                                 verbose=1)
    folds = StratifiedKFold(shuffle=True, random_state=42)
    # モデルの性能を示すメトリック
    result = cross_validate(clf, X, y,
                            cv=folds,
                            return_estimator=True,
                            n_jobs=-1)
    # 学習済みモデル
    estimators = result.pop('estimator')

    #
    mlflow.set_tracking_uri("http://10.255.0.2:5000")

    # 結果を記録する Run を始める
    with mlflow.start_run():

        # 実験に使った Parameter を記録する
        mlflow.log_params({
            'n_estimators': clf.n_estimators,
            'random_state': clf.random_state,
        })

        # 実験で得られた Metric を記録する
        for key, value in result.items():
            # 数値なら int/float な必要があるので平均値に直して書き込む
            mlflow.log_metric(key=key,
                              value=value.mean())

        # 実験で得られた Artifact を記録する
        for index, estimator in enumerate(estimators):

            # 一時ディレクトリの中に成果物を書き出す
            with tempfile.TemporaryDirectory() as d:

                # 学習済みモデル
                clf_filename = f'sklearn.ensemble.RandomForestClassifier.{index}'
                clf_artifact_path = pathlib.Path(d) / clf_filename
                with open(clf_artifact_path, 'wb') as fp:
                    pickle.dump(estimator, fp)

                # 特徴量の重要度
                imp_filename = f'sklearn.ensemble.RandomForestClassifier.{index}.feature_importances_.json'  # noqa
                imp_artifact_path = pathlib.Path(d) / imp_filename
                with open(imp_artifact_path, 'w') as fp:
                    importances = dict(zip(feature_names, estimator.feature_importances_))
                    json.dump(importances, fp, indent=2)

                # ディレクトリにあるファイルを Artifact として登録する
                mlflow.log_artifacts(d)


if __name__ == '__main__':
    main()
