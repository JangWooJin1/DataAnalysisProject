import MySQLdb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

connection = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='1234',
    db='dataProject'
)
cursor = connection.cursor()

data_list_query = """
    SELECT title
    FROM notice
"""
cursor.execute(data_list_query)
data = cursor.fetchall()
data = [notice[0] for notice in data]  # 데이터 형식에 맞게 수정

# TF-IDF 벡터화
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(list(data))

# # Elbow Method를 사용하여 적절한 클러스터 개수 k 결정
# inertias = []
# k_values = range(120, 150)
# for k in k_values:
#     kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
#     kmeans.fit(X)
#     inertias.append(kmeans.inertia_)
#
# print("여기까지 잘됨")
#
# # Elbow Method를 시각화하여 적절한 k 결정
# plt.plot(k_values, inertias, 'bx-')
# plt.xlabel('Number of Clusters (k)')
# plt.ylabel('Inertia')
# plt.title('Elbow Method')
# plt.show()

# 사용자로부터 적절한 클러스터 개수 k 입력
k = int(input("Enter the number of clusters (k): "))

# K-means 클러스터링
kmeans = KMeans(n_clusters=k, random_state=42)
kmeans.fit(X)

# 각 공지사항에 대한 클러스터 할당
labels = kmeans.labels_

# 클러스터별로 공지사항 그룹화
clusters = {}
for i, label in enumerate(labels):
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(data[i])

# # 클러스터별로 그룹화된 공지사항 출력
# for label, notices in clusters.items():
#     print(f"Cluster {label}:")
#     for notice in notices:
#         print(notice)
#     print()

# 사용자가 직접 라벨을 지정
cluster_labels = {}
for label, notices in clusters.items():
    print(f"Cluster {label}:")
    for i, notice in enumerate(notices):
        print(f"{i+1}: {notice}")
    user_label = input("Enter the label for this group: ")
    cluster_labels[label] = user_label
    print()

# 각 공지사항에 라벨링 적용
notice_labels = {}
for i, label in enumerate(labels):
    notice_labels[data[i]] = cluster_labels[label]

# 공지사항에 대한 라벨링 결과 출력
for notice, label in notice_labels.items():
    print(f"{notice}: {label}")