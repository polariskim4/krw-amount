import streamlit as st
import yfinance as yf

# 페이지 설정
st.set_page_config(page_title="주식 매수 계산기", layout="centered")

# CSS: 종목명 줄바꿈 및 Metric 레이아웃 최적화
st.markdown("""
    <style>
    [data-testid="stMetricValue"] div {
        font-size: 1.2rem !important;
        white-space: normal !important;
        word-break: keep-all !important;
        line-height: 1.2 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 주식 매수 원화 계산기")

# 사용자 입력
ticker_input = st.text_input("종목 티커 입력 (예: NVDA, SOXL, AAPL)", value="NVDA").upper()
quantity = st.number_input("수량 입력 (정수)", min_value=1, value=1, step=1)

if st.button("계산하기"):
    try:
        # 1. 주식 데이터 가져오기
        stock = yf.Ticker(ticker_input)
        
        # 2. 가격 추출 로직 (가장 견고한 순서대로 시도)
        current_price = None
        
        # 실시간가 -> 이전 종가 -> 최근 히스토리 순으로 확인
        info = stock.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        
        if current_price is None:
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]

        # 3. 환율 데이터 가져오기
        exchange = yf.Ticker("USDKRW=X")
        # 환율도 info가 실패할 경우를 대비해 history 병행
        usd_krw_rate = exchange.info.get('regularMarketPrice')
        if usd_krw_rate is None:
            ex_hist = exchange.history(period="1d")
            if not ex_hist.empty:
                usd_krw_rate = ex_hist['Close'].iloc[-1]

        # 4. 결과 출력
        if current_price and usd_krw_rate:
            stock_name = info.get('longName') or ticker_input
            total_krw = current_price * quantity * usd_krw_rate

            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("종목명", stock_name)
                st.metric("수량", f"{int(quantity):,} 주")
            
            with col2:
                st.metric("현재 환율", f"{usd_krw_rate:,.1f} 원/$")
                st.metric("원화 총액", f"{int(total_krw):,} 원")

            # f-string 포맷팅 수정: {변수:포맷} 형태여야 합니다.
            st.success(f"현재 {stock_name} ({ticker_input})의 주당 가격은 ,.2f입니다.")
        else:
            st.error("가격을 가져올 수 없습니다. 티커를 확인하거나 잠시 후 다시 시도해주세요.")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
