import streamlit as st
import yfinance as yf

# 페이지 설정
st.set_page_config(page_title="주식 매수 계산기", layout="centered")

# 긴 종목명 줄바꿈을 위한 최소한의 CSS
st.markdown("""
    <style>
    [data-testid="stMetricValue"] div {
        font-size: 1.2rem !important;
        white-space: normal !important;
        word-break: keep-all !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 주식 매수 원화 계산기")

# 사용자 입력
ticker_input = st.text_input("종목 티커 입력 (예: TSLA, NVDA, AAPL)", value="TSLA").upper()
quantity = st.number_input("수량 입력 (정수)", min_value=1, value=1, step=1)

if st.button("계산하기"):
    try:
        # 1. 주식 객체 생성
        stock = yf.Ticker(ticker_input)
        
        # 2. 가격 데이터 가져오기 (가장 안정적인 history 방식 사용)
        # 장 중에는 실시간가, 장 종료 후에는 직전 종가를 가져옵니다.
        df = stock.history(period="1d")
        
        if not df.empty:
            current_price = float(df['Close'].iloc[-1])
        else:
            # history가 실패할 경우 fast_info에서 시도
            current_price = stock.fast_info.get('last_price')

        # 3. 환율 데이터 가져오기 (USD/KRW)
        exchange = yf.Ticker("USDKRW=X")
        ex_df = exchange.history(period="1d")
        if not ex_df.empty:
            usd_krw_rate = float(ex_df['Close'].iloc[-1])
        else:
            usd_krw_rate = exchange.fast_info.get('last_price')

        # 4. 데이터가 모두 확인된 경우에만 화면에 표시
        if current_price and usd_krw_rate:
            # 종목명 가져오기
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

            # f-string 포맷팅을 엄격하게 적용하여 변수값을 출력합니다.
            price_text = f",.2f"
            st.success(f"현재 {stock_name} ({ticker_input})의 주당 가격은 {price_text}입니다.")
        else:
            st.warning("데이터를 가져오는 데 실패했습니다. 티커를 다시 확인해 주세요.")

    except Exception as e:
        st.error(f"오류가 발생했습니다. 잠시 후 다시 시도해 주세요. (에러: {e})")
