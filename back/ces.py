# 客户端代码（用 requests）
import time
import requests

start = time.time()
response = requests.post(
    'http://localhost:3014/',  # 调用你的Flask服务
    json={
        "board": [[0]*7 for _ in range(6)],
        "who": 1
    }
)
elapsed = time.time() - start

best_col = response.json()['drop']  # 获取AI推荐的列
print(f"最佳落子列: {best_col}")
print(f"延迟: {elapsed:.3f}s ({elapsed*1000:.0f}ms)")