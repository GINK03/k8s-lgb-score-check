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

## Dockerコンテナの作り方
Dockerコンテナの作り方には主義主張の一つに、Docker Fileで動作を定義して、人手のオペレーションを行う方法がございます  

プラスでアドホックなオペレーションをある程度許容する文化というのは必要で、Dockerの中に入ってしまって、様々な環境を構築して、commitしてしまうのもありかと思っています（というか楽です）  

ベストプラクティスは様々な企業文化があるので、それに従うといいでしょうが、雑な方法については[こちら](https://github.com/GINK03/gink03.github.io/blob/master/_posts/configs/2017-12-12-Docker.md)で説明しているので、参考にしていただければ幸いです。

## DockerコンテナのGoogle Cloud Container Registryへの登録

Cloud Container Registryへの登録は、タグが、`asia.gcr.io/${YOUR_PROJECT_NAME}/${CONTAINER_NAME}`となっている必要があるので、
一度、このようにコミットして、別のタグを付けます。  
```console
$ docker commit 44f751eb4c19
sha256:5a60e4460a156f4ca2465f4eb71983fbd040a084116884bcb40e88e3537cdc38
$ docker images
REPOSITORY                                         TAG                 IMAGE ID            CREATED             SIZE
<none>                                             <none>              5a60e4460a15        2 minutes ago       8.39GB
...
$ docker tag 5a60e4460a15 asia.gcr.io/${YOUR_PROJECT_NAME}/${CONTAINER_NAME}
```

**gcrへコンテナのアップロード**  
```console
$ gcloud docker -- push asia.gcr.io/${YOUR_PROJECT_NAME}/${CONTAINER_NAME}:latest
```
今回は、CONTAINER_NAMEは`lightgbm-clf`としました  

※[docker hub](https://hub.docker.com/r/nardtree/lightgbm-clf/)に置いてあるので参考にしてください

## K8Sへのデプロイ

K8Sへのデプロイは、コマンドだと、デプロイ時の進捗の情報が充分でないのでWebUIで行う例を示します。  

GCPのKubernetes Engineにアクセスし、クラスタを作成します。  

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807389-7fcff546-7709-11e8-8060-36e67c1ed009.png">
</div>

Hello World程度であれば少ないリソースでいいのですが、少し余裕を持って多めのリソースを投下します。

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807391-84f38718-7709-11e8-853c-8323d08e9243.png">
</div>

クラスタの作成にはしばらくかかるので、しばらく待ちます。

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807393-8951188e-7709-11e8-9ddd-a801160bc0e0.png">
</div>

コンテナレジストリに登録したご自身のDockerコンテナを指定し、このコンテナの起動に必要な引数を入力します。  

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807394-9074b710-7709-11e8-924d-e322a05049c8.png">
</div>

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807397-97034efc-7709-11e8-874d-d10bacefdd77.png">
</div>

機械学習のモデルと各種依存ライブラリを含んだDockerコンテナはサイズが大きいので、しばらく、待ちます（10分程度）  

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807399-9ee7943e-7709-11e8-9f49-69fb22efb912.png">
</div>

外部に公開するために、IPの割当と、Portのマッピングを行います。  

このとき、サービスタイプはロードバランサーを選択します。  

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807401-a7b0507e-7709-11e8-91e8-5f4864a11314.png">
</div>

外部IPが得られるので、次の項で、実際にアクセスしてみましょう。  

<div align="center">
 <img width="600px" src="https://user-images.githubusercontent.com/4949982/41807407-b6230f3e-7709-11e8-9200-ae5ab6efe85b.png">
</div>

## 実際にアクセスする
　今回はマイクロサービスのデザインパターンにのっとり、jsonでデータをやり取りし、任意のテキスト情報から、そのテキストの映画のレビューとしての⭐の数を予想します。  
  stress-testing.pyで負荷テストを行っています。  
  K8Sの特性としてか、SLAを大幅に超過したときに、httpサーバが応答しなくなってしまうので、これは実運用の際にはよく考えたほうが良さそうです。  
 
**GCP　K8Sで予想する**
```console
$ DOCKER=35.189.146.153 python3 stress-testing.py 
...
{"score": 4.059278052177565} 特殊な映画 クリストファー・ノーランらしさ全開だと感じました。この緊迫感、絶望感、暗さ。ダークナイトを思い出します。昼のシーンが多く画面や映像が暗い訳ではないのですが、な
んとなく雰囲気が暗い。でもこの暗さがいい味を出してます。分かりやすい娯楽映画ばかり観ている人には理解しにくいかも。
elapsed time 18.113281965255737
```
**ローカルのDOCKERで予想する** 
```console
$ DOCKER=localhost python3 stress-testing.py 
...
{"score": 4.059278052177565} 特殊な映画 クリストファー・ノーランらしさ全開だと感じました。この緊迫感、絶望感、暗さ。ダークナイトを思い出します。昼のシーンが多く画面や映像が暗い訳ではないのですが、な
んとなく雰囲気が暗い。でもこの暗さがいい味を出してます。分かりやすい娯楽映画ばかり観ている人には理解しにくいかも。
elapsed time 5.5899786949157715
```

何もチューニングしない状態では、ローカルのほうが早いですね（それはそう）
