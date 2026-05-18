import streamlit as st
import yfinance as yf

# 페이지 설정
st.set_page_config(page_title="주식 매수 계산기", layout="centered")

st.title("📊 주식 매수 원화 계산기")
st.write("티커를 입력하면 현재가와 환율을 적용하여 필요한 원화 금액을 계산합니다.")

# 사용자 입력
ticker_input = st.text_input("종목 티커 입력 (예: AAPL, TSLA, NVDA)", value="AAPL").upper()
quantity = st.number_input("수량 입력 (정수)", min_value=1, value=1, step=1)

if st.button("계산하기"):
    try:
        # 주식 데이터 가져오기
        stock = yf.Ticker(ticker_input)
        stock_info = stock.info
        
        # 가격 정보 가져오기 (가장 기본적인 필드 사용)
        current_price = stock_info.get('currentPrice') or stock_info.get('regularMarketPrice')
        
        # 환율 데이터 가져오기 (USD/KRW)
        exchange_data = yf.Ticker("USDKRW=X")
        usd_krw_rate = exchange_data.fast_info['last_price']

        if current_price:
            # 원화 총액 계산
            total_krw = current_price * quantity * usd_krw_rate
            stock_name = stock_info.get('longName', ticker_input)

            # 결과 화면 출력
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("종목명", stock_name)
                st.metric("수량", f"{int(quantity)} 주")
            
            with col2:
                st.metric("현재 환율", f"{usd_krw_rate:.1f} 원/$")
                st.metric("원화 총액", f"{int(total_krw):,} 원")

            st.success(f"현재 {stock_name}의 주당 가격은 ,.2f입니다.")
        else:
            st.error("가격을 가져올 수 없습니다. 티커를 확인해 주세요.")

    except Exception as e:
        st.error("데이터를 불러오는 중 오류가 발생했습니다.")
