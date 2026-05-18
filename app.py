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
st.write("티커를 입력하면 현재가와 환율을 적용하여 필요한 원화 금액을 계산합니다.")

ticker_input = st.text_input("종목 티커 입력 (예: SOXL, NVDA, AAPL)", value="SOXL").upper()
quantity = st.number_input("수량 입력 (정수)", min_value=1, value=1, step=1)

if st.button("계산하기"):
    try:
        # 1. 주식 데이터 객체 생성
        stock = yf.Ticker(ticker_input)
        
        # 2. 가격 데이터 가져오기 (멀티 레이어 체크)
        current_price = None
        
        # 방법 A: info 데이터 확인
        if stock.info and 'currentPrice' in stock.info:
            current_price = stock.info['currentPrice']
        elif stock.info and 'regularMarketPrice' in stock.info:
            current_price = stock.info['regularMarketPrice']
            
        # 방법 B: info가 실패할 경우 history 사용 (가장 확실함)
        if current_price is None:
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]

        # 3. 환율 데이터 가져오기 (USD/KRW)
        exchange = yf.Ticker("USDKRW=X")
        exchange_hist = exchange.history(period="1d")
        usd_krw_rate = exchange_hist['Close'].iloc[-1] if not exchange_hist.empty else None

        # 데이터가 모두 존재할 때만 계산 진행
        if current_price and usd_krw_rate:
            stock_name = stock.info.get('longName') or ticker_input
            total_krw = current_price * quantity * usd_krw_rate

            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("종목명", stock_name)
                st.metric("수량", f"{int(quantity)} 주")
            
            with col2:
                st.metric("현재 환율", f"{usd_krw_rate:.1f} 원/$")
                st.metric("원화 총액", f"{int(total_krw):,} 원")

            st.success(f"현재 {stock_name} ({ticker_input})의 주당 가격은 ,.2f입니다.")
        else:
            st.error(f"'{ticker_input}'의 가격 정보를 찾을 수 없습니다. 티커가 올바른지, 혹은 현재 Yahoo Finance 서비스가 가능한지 확인해 주세요.")

    except Exception as e:
        st.error(f"데이터 조회 중 오류 발생: {e}")
