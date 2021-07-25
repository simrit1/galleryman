r = lambda: list(map(int, input().split()))
ok = lambda a, b: all(a[i] > b[i] for i in range(3))


n = int(input())
arr = [r() for _ in " " * n]
arr = [sorted(i, reverse=1) for i in arr]

vis = [0] * n
c = 0

for i in range(n):
    if vis[i]:
        continue
    for j in range(i + 1, n):
        if vis[j]:
            continue
        if ok(arr[i], arr[j]):
            vis[j] = 1
    c += 1

print(c)
