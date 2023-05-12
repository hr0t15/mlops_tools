echo "--------------------------------"
echo "すべてのコンテナを停止します"
echo ""
docker container stop $(docker ps -q)

echo "--------------------------------"
echo "すべてのコンテナを削除します"
echo ""
docker container rm $(docker ps -q -a)

echo "--------------------------------"
echo "mlflow-trackingのイメージを削除します"
echo ""
docker image rm mlflow-tracking
#docker image rm $(docker images -q)

echo "--------------------------------"
echo "すべてのボリュームを削除します"
echo ""
docker volume rm $(docker volume ls -q)

#docker builder prune
