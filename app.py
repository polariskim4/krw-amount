import streamlit as st
import yfinance as yf

# 페이지 설정
st.set_page_config(page_title="주식 매수 계산기", layout="centered")

# CSS: 종목명 줄바꿈 및 가독성 개선
st.markdown("""
    <style>
    [data-testid="stMetricValue"] div {
        font-size: 1.4rem !important;
        white-space: normal !important;
        word-break: keep-all !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 주식 매수 원화 계산기")

# 사용자 입력
ticker_input = st.text_input("종목 티커 입력 (예: NVDA, SOXL, AAPL)", value="NVDA").upper()
quantity = st.number_input("수량 입력 (정수)", min_value=1, value=1, step=1)

if st.button("계산하기"):
    try:
        # 1. 주식 데이터 객체 생성
        stock = yf.Ticker(ticker_input)
        
        # 2. 가격 데이터 가져오기 (가장 확실한 history 방식 사용)
        # 장 중에는 현재가, 장 종료 후에는 마지막 종가를 가져옵니다.
        df = stock.history(period="1d")
        
        if not df.empty:
            current_price = df['Close'].iloc[-1]
        else:
            # history가 실패할 경우를 대비한 2차 확인
            current_price = stock.info.get('regularMarketPrice') or stock.info.get('previousClose')

        # 3. 환율 데이터 가져오기 (USD/KRW)
        exchange = yf.Ticker("USDKRW=X")
        ex_df = exchange.history(period="1d")
        usd_krw_rate = ex_df['Close'].iloc[-1] if not ex_df.empty else None

        # 4. 데이터가 모두 존재할 때 결과 출력
        if current_price and usd_krw_rate:
            stock_name = stock.info.get('longName') or ticker_input
            total_krw = current_price * quantity * usd_krw_rate

            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("종목명", stock_name)
                st.metric("수량", f"{int(quantity):,} 주")
            
            with col2:
                st.metric("현재 환율", f"{usd_krw_rate:,.1f} 원/$")
                st.metric("원화 총액", f"{int(total_krw):,} 원")

            # f-string 포맷팅을 {변수:포맷} 형태로 정확히 수정했습니다.
            st.success(f"현재 {stock_name} ({ticker_input})의 주당 가격은 ,.2f입니다.")
        else:
            st.error("가격을 가져올 수 없습니다. 티커가 정확한지 확인해 주세요.")

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
