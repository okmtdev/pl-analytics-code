import pandas as pd
from tabulate import tabulate


# 1. 実際の順位
actual_ranking = [
    "リバプール", "アーセナル", "シティ", "チェルシー", "ニューカッスル",
    "アストン・ヴィラ", "ノッティンガム", "ブライトン", "ボーンマス", "ブレントフォード",
    "フラム", "パレス", "エヴァートン", "ウェストハム", "ユナイテッド",
    "ウルブズ", "トッテナム", "レスター", "イプスウィッチ", "サウサンプトン"
]

# 実際の順位を {チーム名: 順位} の辞書に変換 (1-indexed)
actual_rank_map = {team: rank + 1 for rank, team in enumerate(actual_ranking)}
num_teams = len(actual_ranking)

# 実際のチーム名の最大長を計算 (ヘッダー「チーム名」の長さも考慮)
header_team_name_text = "チーム名"
max_team_name_length = 0
if actual_ranking:
    max_team_name_length = max(len(team) for team in actual_ranking)
max_team_name_length = max(max_team_name_length, len(header_team_name_text))


# 2. CSVファイルパスの指定
csv_file_path = 'predicted_rankings.csv'

# 3. CSVファイルの読み込みとエラーハンドリング
try:
    predicted_df = pd.read_csv(csv_file_path, header=None, dtype=str)
except FileNotFoundError:
    print(f"エラー: ファイル '{csv_file_path}' が見つかりません。")
    print(f"プログラムと同じディレクトリに '{csv_file_path}' という名前でCSVファイルを作成し、再実行してください。")
    print("CSVファイルの形式: 各列に1人ずつの予想順位（チーム名）を1行目から20行目まで記述。ヘッダー行は不要です。")
    exit()
except pd.errors.EmptyDataError:
    print(f"エラー: ファイル '{csv_file_path}' は空です。データが含まれているか確認してください。")
    exit()
except Exception as e:
    print(f"CSVファイルの読み込み中に予期せぬエラーが発生しました: {e}")
    exit()

num_predictors = predicted_df.shape[1]
if num_predictors == 0:
    print(f"エラー: CSVファイル '{csv_file_path}' にデータが含まれていないか、形式が正しくありません。")
    exit()

results_summary = []
print("\n--- 各予想の詳細 ---")

# 4. 各予想者ごとの処理ループ
for i in range(num_predictors):
    predictor_name = f"予想者{i+1}"
    predicted_ranking_list_predictor = predicted_df[i].astype(str).str.strip().tolist()

    if len(predicted_ranking_list_predictor) != num_teams:
        print(f"\n--- {predictor_name} の処理エラー ---")
        print(f"エラー: {predictor_name} の予想チーム数 ({len(predicted_ranking_list_predictor)}) が実際のチーム数 ({num_teams}) と異なります。この予想はスキップします。")
        results_summary.append({
            "predictor": predictor_name,
            "status": f"エラー: チーム数不一致 ({len(predicted_ranking_list_predictor)}チーム)",
            "correct_predictions": "N/A",
            "total_rank_difference": "N/A",
            "average_rank_difference": "N/A"
        })
        continue

    predicted_rank_map_predictor = {team: rank + 1 for rank, team in enumerate(predicted_ranking_list_predictor)}
    correct_predictions_count = 0
    total_absolute_rank_difference = 0
    prediction_details = []

    for actual_rank_idx, actual_team in enumerate(actual_ranking):
        actual_position = actual_rank_idx + 1
        predicted_position_val = predicted_rank_map_predictor.get(actual_team) # 修正：変数名変更

        rank_difference_str = ""
        absolute_difference_for_team = 0
        display_predicted_position = "" # 表示用の予想順位

        if predicted_position_val is not None:
            if actual_position == predicted_position_val:
                correct_predictions_count += 1
            difference = actual_position - predicted_position_val
            absolute_difference_for_team = abs(difference)
            rank_difference_str = f"{difference:+d}"
            display_predicted_position = str(predicted_position_val)
        else:
            print(f"警告 ({predictor_name}): 実際{actual_position}位のチーム '{actual_team}' が予想に含まれていません。最下位({num_teams}位)とみなし順位差を計算します。")
            predicted_position_penalty = num_teams
            difference = actual_position - predicted_position_penalty
            absolute_difference_for_team = abs(difference)
            # rank_difference_str = f"N/A (実際{actual_position}位 vs 予想なしのためペナルティ{num_teams}位)" # 元の長いメッセージ
            rank_difference_str = f"実際{actual_position}位 vs 予想なし({num_teams}位扱い)" # 少し短縮
            display_predicted_position = "N/A (予想なし)"

        total_absolute_rank_difference += absolute_difference_for_team

        prediction_details.append({
            "team": actual_team,
            "actual_rank": actual_position,
            "predicted_rank": display_predicted_position, # 表示用文字列
            "rank_difference_str": rank_difference_str,
            "abs_difference": absolute_difference_for_team
        })

    avg_rank_diff = total_absolute_rank_difference / num_teams if num_teams > 0 else 0
    results_summary.append({
        "predictor": predictor_name,
        "status": "成功",
        "correct_predictions": correct_predictions_count,
        "total_rank_difference": total_absolute_rank_difference,
        "average_rank_difference": avg_rank_diff
    })

    # 5. 各予想者の詳細結果の表示
    print(f"\n--- {predictor_name} の詳細 ---")
    print(f"的中数（順位とチーム名が完全に一致）: {correct_predictions_count} / {num_teams}")
    print(f"合計順位差の絶対値: {total_absolute_rank_difference}")
    print(f"平均順位差の絶対値: {avg_rank_diff:.2f}")
    print("各チームの比較:")

    headers = ["チーム名", "実際順位", "予想順位", "順位差(実際-予想)", "差の絶対値"]
    rows = [
        [d['team'],
         d['actual_rank'],
         d['predicted_rank'] or "N/A",
         d['rank_difference_str'],
         d['abs_difference']] 
        for d in prediction_details
    ]

    print(tabulate(rows, headers=headers, tablefmt="pretty", stralign="left"))

# 6. 総合サマリーの表示 (変更なし)
print("\n\n--- 🏆 総合サマリー (平均順位差が小さい順) ---")
results_summary.sort(key=lambda x: (
    0 if x['status'] == '成功' else 1,
    x.get('average_rank_difference', float('inf')) if x['status'] == '成功' else float('inf')
))

print(f"{'予想者':<10} | {'的中数':<5} | {'合計順位差':<10} | {'平均順位差':<10} | {'ステータス':<20}")
print("-" * 70) # この区切り線も必要であれば総合サマリーのヘッダー長に合わせても良い
for result in results_summary:
    if result['status'] == '成功':
        avg_diff_str = f"{result['average_rank_difference']:.2f}"
        print(f"{result['predictor']:<10} | {result['correct_predictions']:<5} | {result['total_rank_difference']:<10} | {avg_diff_str:<10} | {result['status']:<20}")
    else:
        print(f"{result['predictor']:<10} | {'N/A':<5} | {'N/A':<10} | {'N/A':<10} | {result['status']:<20}")