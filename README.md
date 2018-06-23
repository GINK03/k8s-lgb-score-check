# TODO

- モデルを含んだDockerコンテナの作成
- Google Container Registryへの配置
- k8sサービスに乗せる

- (必要ならばk8sのパラメータチューニング)


# K8Sで機械学習の予想システムを作成する　　

**目次**  
 - 今の機械学習のシステムの粒度はDocker
 - Dockerのデプロイ先としてのK8S
 - Dockerコンテナの作り方
 - DockerコンテナのGoogle Cloud Container Registryへの登録
 - K8Sへのデプロイ
 - 実際にアクセスする


## K8Sへのデプロイ

K8Sへのデプロイは、コマンドだと、デプロイ時の進捗の情報が充分でないのでWebUIで行う例を示します。  

GCPのKubernetes Engineにアクセスし、クラスタを作成します。  

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807389-7fcff546-7709-11e8-8060-36e67c1ed009.png">
</div>

Hello World程度であれば少ないリソースでいいのですが、少し余裕を持って多めのリソースを投下します。
