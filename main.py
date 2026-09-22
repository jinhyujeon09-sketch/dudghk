import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # 개봉일: 여덟 자리 숫자 -> datetime
    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")

    # 장르: 세로막대(|) 기호로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).apply(lambda x: x.split("|")[0].strip())

    return df


def insight_box(text: str):
    """그래프 아래 '이 그래프로 알 수 있는 것' 자리를 만들어 준다."""
    st.markdown("**💡 이 그래프로 알 수 있는 것**")
    st.info(text)


# ---------------------------------------------------------
# 앱 시작
# ---------------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 가운데, 이 기간에 개봉한 216편의 데이터를 살펴봅니다."
)

df = load_data(DATA_URL)

with st.expander("원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ===========================================================
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# ===========================================================
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .rename_axis("genre")
    .reset_index(name="count")
)

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.55,
)
fig_genre.update_traces(
    textinfo="label+percent",
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_genre, use_container_width=True)

insight_box(
    f"216편 중 가장 많은 장르는 '{genre_counts.iloc[0]['genre']}'({int(genre_counts.iloc[0]['count'])}편)이며, "
    "장르별 편수 분포를 통해 어떤 장르가 박스오피스 10위권에 자주 진입하는지 알 수 있습니다."
)

st.divider()

# ===========================================================
# 그래프 2. 장르 안의 영화들 - 트리맵 (칸 크기 = 총 관객)
# ===========================================================
st.header("2. 장르별 영화 흥행 트리맵")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_treemap, use_container_width=True)

top_movie = df.loc[df["total_audi"].idxmax()]
insight_box(
    f"장르 안에서 각 영화가 차지하는 칸의 크기가 총 관객 수를 나타내며, "
    f"전체에서 가장 큰 칸은 '{top_movie['movieNm']}'(총 관객 {int(top_movie['total_audi']):,}명)입니다. "
    "이를 통해 어떤 장르에 흥행작이 몰려 있는지 한눈에 볼 수 있습니다."
)

st.divider()

# ===========================================================
# 그래프 3. 총 관객 히스토그램
# ===========================================================
st.header("3. 총 관객(total_audi) 히스토그램")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
)
fig_hist.update_traces(
    hovertemplate="총 관객 구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 수",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_hist, use_container_width=True)

hist_counts, hist_edges = np.histogram(df["total_audi"], bins=30)
max_bin_idx = hist_counts.argmax()
bin_low, bin_high = hist_edges[max_bin_idx], hist_edges[max_bin_idx + 1]

insight_box(
    f"대부분의 영화는 총 관객 약 {int(bin_low):,}명 ~ {int(bin_high):,}명 구간에 몰려 있으며, "
    f"가장 관객이 많았던 영화는 '{top_movie['movieNm']}'(총 관객 {int(top_movie['total_audi']):,}명)입니다."
)

st.divider()

# ===========================================================
# 그래프 4. 개봉일 스크린수 vs 총 관객 - 산점도
# ===========================================================
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
)
fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_scatter, use_container_width=True)

corr = df["first_scrn"].corr(df["total_audi"])
insight_box(
    f"개봉일 스크린수와 총 관객 수 사이의 상관계수는 약 {corr:.2f}로, "
    "스크린을 많이 확보할수록 총 관객도 많아지는 경향이 있지만 장르에 따라 예외도 눈에 띕니다."
)

st.divider()

# ===========================================================
# 그래프 5. 영화 10편 이상인 장르 - 총 관객 박스플롯
# ===========================================================
st.header("5. 장르별 총 관객 분포 (10편 이상 장르)")

valid_genres = genre_counts.loc[genre_counts["count"] >= 10, "genre"]
df_box = df[df["genre"].isin(valid_genres)]

fig_box = px.box(
    df_box,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
)
fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_box, use_container_width=True)

median_by_genre = df_box.groupby("genre")["total_audi"].median().sort_values(ascending=False)
insight_box(
    f"영화가 10편 이상인 장르 중에서는 '{median_by_genre.index[0]}' 장르의 총 관객 중앙값이 가장 높고, "
    "상자 밖으로 튀는 점들은 해당 장르에서 유난히 흥행했거나 부진했던 영화들을 보여줍니다."
)

st.divider()

# ===========================================================
# 그래프 6. 스크린수 x 총 관객 x 첫 주 관객 - 버블 그래프
# ===========================================================
st.header("6. 스크린수·총 관객·첫 주 관객 버블 그래프")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
)
fig_bubble.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_bubble, use_container_width=True)

biggest_bubble = df.loc[df["first_week_audi"].idxmax()]
insight_box(
    f"버블 크기는 첫 주 관객 수를 나타내며, 가장 큰 버블은 '{biggest_bubble['movieNm']}'"
    f"(첫 주 관객 {int(biggest_bubble['first_week_audi']):,}명)입니다. "
    "스크린수와 총 관객이 비슷해도 첫 주 흥행 속도는 영화마다 다르다는 것을 알 수 있습니다."
)

st.divider()

# ===========================================================
# 그래프 7. 제작 국가 -> 장르 - 선버스트 그래프
# ===========================================================
st.header("7. 제작 국가별 장르 구성 - 선버스트 그래프")

fig_sunburst = px.sunburst(
    df,
    path=["nation", "genre"],
)
fig_sunburst.update_traces(
    hovertemplate="%{label}<br>영화 수: %{value}편<extra></extra>",
)
fig_sunburst.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_sunburst, use_container_width=True)

top_nation = df["nation"].value_counts().index[0]
insight_box(
    f"'{top_nation}'이(가) 가장 많은 편수를 배출한 제작 국가이며, "
    "국가 안쪽 칸을 통해 각 나라가 어떤 장르의 영화를 주로 흥행권에 올렸는지 확인할 수 있습니다."
)

st.divider()
