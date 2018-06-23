
# K8Sで機械学習の予想システムを作成　　

**目次**  
 - 機械学習の最小粒度としてのDocker, Dockerのデプロイ先としてのk8s
 - テキストを評価するAPIのDockerコンテナの作り方
 - DockerコンテナのGoogle Cloud Container Registryへの登録
 - K8Sへのデプロイ
 - 実際にアクセスする
 - まとめ

## 機械学習の最小粒度としてのDocker, Dockerのデプロイ先としてのk8s
 コンテナのオーケストレーションツールがk8sが他のツールを押しのけて、優位にたった状況からしばらく経過し、ドキュメントやユースケースが揃ってきました。  
 
 GCPではコンテナを使ったデプロイメントサービスはKubernetes Engineがデフォルトであり、WebUIやCUIでの操作例を示したドキュメントも充実してきました。  
 k8sは、ローリングリリースが簡単にできたり、分析者からDocker Fileやコンテナが適切に受け渡しが開発者に行われれば、デプロイまでの時間的労力的消耗を最小化できたりします。  
 
 また、Micro Serviceのデザインパターンとして、Dockerが一つの管理粒度になり、そこだけで閉じてしまえば、自分の責任範囲を明確にし、役割が明確になり、**「分析 ->  モデルの評価＆作成 -> IFの定義 -> コード作成 -> Dockerに固める」**　というプロセスに落とすことができ、進捗も良くなります。  
 
 今回はjson形式で日本語の自然言語を受け取り、映画のレビューだとした場合、星がいくつなのがを予想するトイプロブレムをk8sに実際にデプロイして使ってみるまでを説明します。  
 
 今回のk8sのデザインはこのようなスタイルになります。  
<div align="center">
  <img width="550px" src="https://user-images.githubusercontent.com/4949982/41809085-7a17abe4-7722-11e8-8895-f7d43cad01e9.png">
</div>

## テキストを評価するAPIのDockerコンテナの作り方

**予想モデルの要件**
- 任意のテキストをhttp経由でjsonを受け取る
- テキストを分かち書きし、ベクトル化する
- ベクトル化した情報に基づき、テキストが映画レビューならば、レビューの星何個に該当するか予想する
- 予想した星の数をhttp経由でjsonで返却する
- 以上の挙動をする仕組みをDockerコンテナとして提供する

HTTPサーバは私の以前の[JSONのやりとりの個人プロジェクト](https://github.com/GINK03/loose-coupling-json-over-http)を参照しています。  

予想システムは映画.comさまのコーパスを利用して、LightGBMでテキストコーパスから予想を行います。学習と評価に使った[スクリプトとコーパスはこちら](https://github.com/GINK03/k8s-lgb-score-check/tree/master/train-corpus)になります。  


**Dockerコンテナに集約する**  

　以前作成した何でも[ごった煮Dockerがコンテナ](https://hub.docker.com/r/nardtree/oppai/)があり、それを元に編集して作成しました。  

　本来ならば、Docker Fileを厳密に定義して、Docker Fileからgithubからpullして、システムの/usr/binに任意のスクリプトを配置する記述をする必要があります。  
 
　それとは別に、アドホックなオペレーションをある程度許容する方法も可能ではあり、Dockerの中に入ってしまって、様々な環境を構築して、commitしてしまうのもありかと思っています（というか楽ですので、それで対応しました）  

　ベストプラクティスは様々な企業文化があるので、それに従うといいでしょうが、雑な方法については[こちら](https://github.com/GINK03/gink03.github.io/blob/master/_posts/configs/2017-12-12-Docker.md)で説明しているので、参考にしていただければ幸いです。

　作成したDockerコンテナは[こちら](https://hub.docker.com/r/nardtree/lightgbm-clf/)
 
 動作はこのようにローカルで行えます。  
 
```console
$ docker pull nardtree/lightgbm-clf
$ docker run -it nardtree/lightgbm-clf 40-predict.py
```

**挙動のチェック**  

ポジティブな文を投入してみる
```console
$ curl -v -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"texts":"すごい！最高に興奮した！楽しい"}'  http://localhost:4567/api/1/users
{"score": 4.77975661771051}
```
(星５が最高なので、ほぼ最高)

ネガティブな文を投入してみる
```console
$ curl -v -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"texts":"この映画は全くだめ、楽しくない。駄作"}' http://localhost:4567/api/1/users
{"score": 1.2809874000768104}
```
(星1が最低)

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
  stress-testing.pyで1000件の自然言語のコーパスに対して、負荷テストを行っています。  
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

## まとめ

Dockerで簡潔にかつ素早くサービスを提供する仕組みを提供する仕組みとしてとても良いと思います。  

小さい案件を一瞬で終わらせるデザインパターンとして、有益なように思います。  

