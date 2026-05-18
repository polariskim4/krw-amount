import streamlit as st
import yfinance as yf

# 페이지 설정
st.set_page_config(page_title="주식 매수 계산기", layout="centered")

st.title("📊 주식 매수 원화 계산기")
st.write("장이 종료된 시간에도 마지막 종가를 기준으로 계산합니다.")

# 사용자 입력
ticker_input = st.text_input("종목 티커 입력 (예: NVDA, SOXL, AAPL)", value="NVDA").upper()
quantity = st.number_input("수량 입력 (정수)", min_value=1, value=1, step=1)

if st.button("계산하기"):
    try:
        # 1. 주식 데이터 가져오기
        stock = yf.Ticker(ticker_input)
        
        # 2. 가격 데이터 가져오기 (가장 확실한 history 방식 사용)
        # 장 중에는 현재가, 장 종료 후에는 마지막 종가를 가져옵니다.
        df = stock.history(period="1d")
        if not df.empty:
            current_price = df['Close'].iloc[-1]
        else:
            # history가 실패할 경우 info에서 대체값 확인
            current_price = stock.info.get('regularMarketPrice') or stock.info.get('previousClose')

        # 3. 환율 데이터 가져오기 (USD/KRW)
        exchange = yf.Ticker("USDKRW=X")
        ex_df = exchange.history(period="1d")
        usd_krw_rate = ex_df['Close'].iloc[-1] if not ex_df.empty else None

        if current_price and usd_krw_rate:
            # 종목명 (info가 비어있을 수 있으므로 안전하게 처리)
            stock_name = stock.info.get('longName') or ticker_input
            
            # 원화 총액 계산
            total_krw = current_price * quantity * usd_krw_rate

            # 결과 화면 출력
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("종목명", stock_name)
                st.metric("수량", f"{int(quantity)} 주")
            
            with col2:
                st.metric("현재 환율", f"{usd_krw_rate:.1f} 원/$")
                st.metric("원화 총액", f"{int(total_krw):,} 원")

            # 하단 상세 정보 안내 (f-string 포맷팅 수정 완료)
            st.success(f"현재 {stock_name} ({ticker_input})의 주당 가격은 ,.2f입니다.")
        else:
            st.error("가격을 가져올 수 없습니다. 티커가 정확한지 확인해 주세요.")

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
