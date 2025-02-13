# GKE

## 前提条件

```
gcloud services enable container.googleapis.com
gcloud components install gke-gcloud-auth-plugin
```

## クラスター作成コマンド

Standard Mode を利用

```
gcloud container clusters create sample-cluster \
 --zone=asia-northeast1-a \
 --num-nodes=2 \
 --machine-type=e2-small \
 --enable-autoscaling --min-nodes=1 --max-nodes=2 \
 --disk-size=10 \
 --disk-type=pd-standard \
 --enable-ip-alias \
 --preemptible

```

Google Cloud で利用できる 最も安価なマシンタイプ は e2-micro や e2-small ですが、GKE の運用では 最低でも e2-medium 以上が推奨 されます。

マシンタイプ vCPU メモリ 料金（東京リージョン）
e2-micro 0.25 1GB 無料枠対象 -> GKE では動作が厳しい（負荷がかかるとすぐ OOM）
e2-small 0.5 2GB 約 $7.73/月 -> 軽量なワークロードなら十分
e2-medium 1 4GB 約 $15.46/月 -> 安定しているがコストが倍になる
👉 推奨 e2-small

- --machine-type=e2-small: コストを抑えつつ、最低限の動作ができる
- --num-nodes=2: ノード数を最小限に（3→2）
- --enable-autoscaling --min-nodes=1 --max-nodes=2: 負荷が低いときにノードを減らしてコスト削減
- --disk-size=10: デフォルト（100GB）→ 10GB に縮小してコスト削減
- --disk-type=pd-standard: SSD（pd-ssd）ではなく HDD (pd-standard) を選択
- --preemptible: スポットインスタンス（プリエンプティブ VM）を使用し、大幅にコスト削減。約 80%安い ので実験環境に最適（ただし突然削除される可能性あり）

## クラスター情報確認

クラスター一覧を表示

```
gcloud container clusters list
```

特定のクラスターの詳細情報を表示

```
gcloud container clusters describe sample-cluster --zone=asia-northeast1-a
```

クラスターに接続して詳細情報を kubectl で確認

```
gcloud container clusters get-credentials sample-cluster --zone=asia-northeast1-a
```

クラスターヘルス

```
kubectl cluster-info
```

## リソース確認

全ての Pod を確認

```
kubectl get pods -A
```

システム Pod を確認

```
kubectl get pods -n kube-system
```

ノード一覧の確認

```
kubectl get nodes -o wide
```

ノードリソースの使用状況

```
kubectl top nodes
```

## リソース適用

ネームスペース

```
kubectl create namespace ngin
```

```
kubectl apply -f manifests/deployment.yaml
kubectl get deployments
kubectl describe deployment my-app
```

```
kubectl logs my-app-86d5bc587d-6qw95 -n default

for pod in $(kubectl get pods -l app=my-app -n default -o jsonpath='{.items[*].metadata.name}'); do
  echo "Logs for $pod:"
  kubectl logs $pod -n default
done
```

```
kubectl apply -f manifests/service.yaml
kubectl get services
kubectl describe service my-app-service
```

## ロードバランサーの用意

```
kubectl expose deployment my-app --type=LoadBalancer --port=80 --target-port=80
```

Service を LoadBalancer にすると GCP の外部ロードバランサーが自動で作成される

```
kubectl get services my-app-service
```

## クラスター削除コマンド

```
gcloud container clusters delete sample-cluster --zone=asia-northeast1-a
```

ロードバランサーが削除されずに残っている場合

```
gcloud compute forwarding-rules list
gcloud compute forwarding-rules delete <FORWARDING_RULE_NAME>
```
