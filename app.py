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
st.write("실시간 주가와 환율을 바탕으로 필요한 원화 금액을 계산합니다.")

# 사용자 입력
ticker_input = st.text_input("종목 티커 입력 (예: AAPL, TSLA, NVDA)", value="AAPL").upper()
quantity = st.number_input("수량 입력 (정수)", min_value=1, value=1, step=1)

if st.button("계산하기"):
    try:
        # 1. 주식 데이터 가져오기 (가장 안정적인 history 메서드 사용)
        stock = yf.Ticker(ticker_input)
        df = stock.history(period="1d")
        
        if not df.empty:
            # 최근 종가를 가져와 숫자로 변환
            current_price = float(df['Close'].iloc[-1])
            
            # 2. 환율 데이터 가져오기 (USD/KRW)
            exchange = yf.Ticker("USDKRW=X")
            ex_df = exchange.history(period="1d")
            usd_krw_rate = float(ex_df['Close'].iloc[-1]) if not ex_df.empty else 1350.0  # 실패 시 기본값

            # 3. 데이터 처리
            stock_name = stock.info.get('longName') or ticker_input
            total_krw = current_price * quantity * usd_krw_rate

            # 4. 화면 출력용 문자열 미리 생성 (f-string 오류 원천 차단)
            formatted_price = "${:,.2f}".format(current_price)
            formatted_total = "{:,.0f} 원".format(total_krw)
            formatted_rate = "{:,.1f} 원/$".format(usd_krw_rate)

            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("종목명", stock_name)
                st.metric("수량", "{:,} 주".format(int(quantity)))
            
            with col2:
                st.metric("현재 환율", formatted_rate)
                st.metric("원화 총액", formatted_total)

            # 성공 메시지 출력
            st.success("현재 {} ({})의 주당 가격은 {}입니다.".format(stock_name, ticker_input, formatted_price))
        
        else:
            st.error("티커를 찾을 수 없거나 가격 정보를 가져올 수 없습니다. 티커를 다시 확인해 주세요.")

    except Exception as e:
        st.error("데이터를 처리하는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")

