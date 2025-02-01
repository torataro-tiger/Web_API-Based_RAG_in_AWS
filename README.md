# Web_API-Based_RAG_in_AWS
AWSでのBedrockとKendraによるRAGアーキテクチャ。備忘録として記載。

## AWS構成図
![](/images/aws_structure.png)
- API GatewayでIP制限を実施し、自分のみ使えるようにする。
- 本当はBedrockも`"ap-northeast-1"`で完結させたかったが、レスポンスに時間がかかりAPI Gatewayがタイムアウトになる。従ってBedrockのみ`"us-east-1"`のものを使う。なぜか遠い地のほうが早い。
- LambdaはECRからコンテナベースでデプロイ。Lambda Layerベースでデプロイするとzip化したモジュールの容量制限が50MB、展開時が250MBなのでなかなか自由がきかない。

### コメント
完全なWebアプリケーションとして動作させるのであれば、S3でのフロントのホスティング、CloudFrontやWAFの設置が必要となる。一旦その前段階としてAPI Gatewayで直接やり取りを行うアーキテクチャを構築。

## ローカルでの実行方法
### 前提環境
- Docker Desktopでのコンテナ管理
- Git Bashでのコマンド実行
- Kendraはインデックス作成済み。データソースはS3でおいて`Kendra_testdata`の中のファイルをS3にアップロード。データソースとS3の同期は実施済み。
- `"us-east-1"`のBedrockでモデル`"anthropic.claude-3-sonnet-20240229-v1:0"`が使えること

### 準備(ローカル側)
`container`ディレクトリに以下の内容の`settings.py`を作成する。
`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`にはKendraのインデックスIDが入る。
```python
from typing import Final

INDEX_ID: Final = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### 環境変数の設定
```
export AWS_ACCESS_KEY_ID=XXXXX \
export AWS_SECRET_ACCESS_KEY=XXXXX \
export IMAGE_NAME=XXXXX
```
### ビルド方法
```
docker build -t ${IMAGE_NAME} .
```
### コンテナ実行方法
初期コンテナ実行
```
docker run --rm \
  -p 9000:8080 \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  ${IMAGE_NAME}
```
再度実行したいときは以下のコマンドをたたく。
```
docker rmi ${IMAGE_NAME}; \
docker build -t ${IMAGE_NAME} .; \
docker run --rm \
  -p 9000:8080 \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  ${IMAGE_NAME}
```
### キャッシュ全削除
イメージ作ってコンテナ実行して削除を繰り返すとキャッシュがたまるので定期的にクリアする。
```
docker system prune --volumes
```
### コマンド実行方法
request.jsonに質問内容を記述し、以下のコマンドを実行。
```
curl -X POST \
  -H "Content-Type: application/json; charset=UTF-8" \
  -d @request.json \
  http://localhost:9000/2015-03-31/functions/function/invocations
```
コマンド実行結果例
```
> Entering new AgentExecutor chain...
Thought: ローマの今日の天気を知るには、weather_searchツールを使って検索する必要があります。
Action: weather_search
Action Input: ローマの今日の天気Document Title: 天気3.csv
Document Excerpt:
地域 国 今日の天気 最高気温(°C) 最低気温(°C) 東京 日本 曇り 10 1 大阪 日本 曇り 10 1 札幌 日本 小雪 -2 -10 ニューヨーク アメリカ合衆国 曇り 5 -1 ロンドン イギリス 晴れ 5 -1 パリ フランス 霧 5 -3 北京 中国 晴れ 6 -6 シドニー オーストラリア 晴れたり曇ったり 25 17 サンパウロ ブラジル 雷雨 28 20 ヨハネスブルグ 南アフリカ共和国 雷雨 26 16


Document Title: 天気1.txt
Document Excerpt:
1. ローマ, イタリア - 晴れ, 最高気温 12°C, 最低気温 4°C 2. ドバイ, アラブ首長国連邦 - 晴れ, 最高気温 26°C, 最低気温 17°C 3. モスクワ, ロシア - 雪, 最高気温 -5°C, 最低気温 -12°C 4. リオデジャネイロ, ブラジル - 曇り時々晴れ, 最高気温 30°C, 最低気温 23°C 5. バンクーバー, カナダ - 雨, 最高気温 7°C, 最低気温 2°C 6. メルボルン, オーストラリア - 曇り, 最高気温 22°C, 最低気温 15°C 7. ヨハネスブルグ, 南アフリカ - 晴れ時々雷雨, 最高気温 27°C, 最低気温 18°C 8.


Document Title: 天気1.txt
Document Excerpt:
モスクワ, ロシア - 雪, 最高気温 -5°C, 最低気温 -12°C 4. リオデジャネイロ, ブラジル - 曇り時々晴れ, 最高気温 30°C, 最低気温 23°C 5. バンクーバー, カナダ - 雨, 最高気温 7°C, 最低気温 2°C 6. メルボルン, オーストラリア - 曇り, 最高気温 22°C, 最低気温 15°C 7. ヨハネスブルグ, 南アフリカ - 晴れ時々雷雨, 最高気温 27°C, 最低気温 18°C 8. カイロ, エジプト - 晴れ, 最高気温 20°C, 最低気温 12°C 9. メキシコシティ, メキシコ - 曇り, 最高気温 21°C, 最低気温 10°C 10. バンコク, タイ - 曇り時々雨, 最高気温 33°C, 最低気温 25°C
検索結果から、ローマの今日の天気は晴れで、最高気温は12度、最低気温は4度であることがわかりました。

Final Answer: ローマの今日の天気は晴れで、最高気温は12度、最低気温は4度です。

> Finished chain.
```

## AWS関連（要所要所のポイント）
### Lambda
LambdaからBedrockとKendraにアクセスするので構築したLambdaに以下のIAMロールを追加
- BedrockFullAccess
- KendraFullAccess

構築時のアーキテクチャは`x86_64`で設定。(`public.ecr.aws/lambda/python:3.12`の場合)

### ECR
構築時はAWS KMSを選択およびAWSマネージドキーを選択。構築したら後はコンテナイメージをローカルからプッシュ

### API Gateway
構築自体は難しくない。LambdaトリガーをAPI Gatewayで設定すれば基本的に問題ない。ただしIP制限のため以下のリソースポリシーを設定。
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "execute-api:/*/*/*"
    },
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "execute-api:/*/*/*",
      "Condition": {
        "NotIpAddress": {
          "aws:SourceIp": [
            "[許可したいグローバルIPアドレス]"
          ]
        }
      }
    }
  ]
}
```
参考: https://blog.logical.co.jp/entry/2022/05/10/120000

#### 注意点
API Gatewayの統合リクエストのタイムアウトはデフォルトだと最大29秒。もしこれを緩和したい場合はAWS側へ申請する必要があり。

### コマンド実行方法
```
curl -X POST \
  -H "Content-Type: application/json; charset=UTF-8" \
  -d @request.json \
  [API Gatewayで作成したWeb APIのURL]
```
レスポンス例
```
{"input": "ローマの今日の天気を教えて？", "output": "ローマの今日の天気は晴れで、最高気温は12度、最低気温は4度です。"}
```

### 後片づけ
**ECSのリポジトリとKendraのIndexはそのままにすると課金対象なので使い終わったら削除すること！！特にKendraはDeveloper Editionでも一か月放置すると13万程度取られる。**