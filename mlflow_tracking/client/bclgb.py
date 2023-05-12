#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mlflow
from mlflow import lightgbm as mlflow_lgb
import numpy as np
import lightgbm as lgb
from sklearn import datasets
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def main():
    mlflow.set_tracking_uri("http://10.255.0.2:5000")
    # LightGBM の学習を自動でトラッキングする
    mlflow_lgb.autolog()

    # データセットを読み込む
    dataset = datasets.load_breast_cancer()
    X, y = dataset.data, dataset.target
    feature_names = list(dataset.feature_names)

    # 訓練データと検証データに分割する
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        shuffle=True,
                                                        random_state=42)

    # データセットを生成する
    lgb_train = lgb.Dataset(X_train, y_train,
                            feature_name=feature_names)
    lgb_eval = lgb.Dataset(X_test, y_test,
                           reference=lgb_train,
                           feature_name=feature_names)

    lgbm_params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'verbosity': -1,
    }
    # ここでは MLflow Tracking がパッチした train() 関数が呼ばれる
    booster = lgb.train(lgbm_params,
                        lgb_train,
                        valid_sets=lgb_eval,
                        num_boost_round=1000,
                        early_stopping_rounds=100,
                        verbose_eval=10,
                        )

    # 学習済みモデルを使って検証データを予測する
    y_pred_proba = booster.predict(X_test,
                                   num_iteration=booster.best_iteration)

    # 検証データのスコアを確認する
    y_pred = np.where(y_pred_proba > 0.5, 1, 0)
    test_score = accuracy_score(y_test, y_pred)
    print(test_score)


if __name__ == '__main__':
    main()
