import streamlit as st
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính lãi suất tiết kiệm",
    page_icon="💰",
    layout="wide"
)

# ============================================================
# HÀM TIỆN ÍCH
# ============================================================

def format_money(value):
    """Định dạng số tiền theo kiểu Việt Nam."""
    value = Decimal(str(value)).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    )
    return f"{int(value):,}".replace(",", ".") + " VNĐ"


def calculate_simple_interest(principal, annual_rate, months):
    """
    Tính lãi đơn.

    Công thức:
    Tiền lãi = Tiền gốc × lãi suất năm × số tháng / 12
    """
    interest = principal * annual_rate / 100 * months / 12
    total = principal + interest

    return interest, total


def calculate_compound_interest(principal, annual_rate, months):
    """
    Tính lãi kép theo kỳ nhập lãi hàng tháng.

    Lãi suất tháng = lãi suất năm / 12
    Tổng tiền = P * (1 + r/12)^n
    """
    monthly_rate = annual_rate / 100 / 12

    total = principal * ((1 + monthly_rate) ** months)
    interest = total - principal

    return interest, total


def calculate_periodic_interest(
    principal,
    annual_rate,
    months,
    interest_type,
    payment_method
):
    """
    Tính tiền lãi theo từng kỳ.

    payment_method:
        - Hàng tháng
        - Hàng quý
        - Cuối kỳ
    """

    # ----------------------------
    # LÃI ĐƠN
    # ----------------------------
    if interest_type == "Lãi đơn":
        total_interest, total_amount = calculate_simple_interest(
            principal,
            annual_rate,
            months
        )

        # Lãi suất năm quy đổi theo tháng
        monthly_interest = principal * annual_rate / 100 / 12

        if payment_method == "Hàng tháng":
            periods = months
            periodic_interest = monthly_interest

        elif payment_method == "Hàng quý":
            periods = months // 3
            periodic_interest = principal * annual_rate / 100 / 4

            # Nếu kỳ hạn không chia hết cho 3 tháng,
            # phần lẻ vẫn được tính theo số tháng thực tế.
            if months % 3 != 0:
                periods += 1

        else:  # Cuối kỳ
            periods = 1
            periodic_interest = total_interest

    # ----------------------------
    # LÃI KÉP
    # ----------------------------
    else:
        total_interest, total_amount = calculate_compound_interest(
            principal,
            annual_rate,
            months
        )

        if payment_method == "Hàng tháng":
            periods = months
            periodic_interest = None

        elif payment_method == "Hàng quý":
            periods = (months + 2) // 3
            periodic_interest = None

        else:  # Cuối kỳ
            periods = 1
            periodic_interest = total_interest

    return {
        "total_interest": total_interest,
        "total_amount": total_amount,
        "periods": periods,
        "periodic_interest": periodic_interest
    }


def create_schedule(
    principal,
    annual_rate,
    months,
    interest_type,
    payment_method
):
    """
    Tạo bảng diễn biến tiền gốc/lãi theo kỳ.
    """

    rows = []

    # ========================================================
    # LÃI ĐƠN
    # ========================================================
    if interest_type == "Lãi đơn":

        monthly_interest = principal * annual_rate / 100 / 12

        if payment_method == "Hàng tháng":

            balance = principal

            for month in range(1, months + 1):
                interest = monthly_interest
                balance += interest

                rows.append({
                    "Kỳ": f"Tháng {month}",
                    "Tiền gốc": principal,
                    "Tiền lãi kỳ này": interest,
                    "Tổng tiền": balance
                })

        elif payment_method == "Hàng quý":

            balance = principal
            current_month = 0

            while current_month < months:
                period_months = min(3, months - current_month)

                interest = (
                    principal
                    * annual_rate
                    / 100
                    * period_months
                    / 12
                )

                balance += interest
                current_month += period_months

                rows.append({
                    "Kỳ": f"Đến tháng {current_month}",
                    "Tiền gốc": principal,
                    "Tiền lãi kỳ này": interest,
                    "Tổng tiền": balance
                })

        else:  # Cuối kỳ

            total_interest = (
                principal
                * annual_rate
                / 100
                * months
                / 12
            )

            rows.append({
                "Kỳ": f"Cuối kỳ ({months} tháng)",
                "Tiền gốc": principal,
                "Tiền lãi kỳ này": total_interest,
                "Tổng tiền": principal + total_interest
            })

    # ========================================================
    # LÃI KÉP
    # ========================================================
    else:

        monthly_rate = annual_rate / 100 / 12
        balance = principal

        if payment_method == "Hàng tháng":

            for month in range(1, months + 1):

                beginning_balance = balance

                interest = beginning_balance * monthly_rate
                balance += interest

                rows.append({
                    "Kỳ": f"Tháng {month}",
                    "Tiền gốc": beginning_balance,
                    "Tiền lãi kỳ này": interest,
                    "Tổng tiền": balance
                })

        elif payment_method == "Hàng quý":

            current_month = 0

            while current_month < months:

                period_months = min(3, months - current_month)

                beginning_balance = balance

                # Cộng dồn lãi theo tháng trong quý
                for _ in range(period_months):
                    interest_month = balance * monthly_rate
                    balance += interest_month

                interest = balance - beginning_balance
                current_month += period_months

                rows.append({
                    "Kỳ": f"Đến tháng {current_month}",
                    "Tiền gốc": beginning_balance,
                    "Tiền lãi kỳ này": interest,
                    "Tổng tiền": balance
                })

        else:  # Cuối kỳ

            beginning_balance = balance

            for _ in range(months):
                interest_month = balance * monthly_rate
                balance += interest_month

            total_interest = balance - beginning_balance

            rows.append({
                "Kỳ": f"Cuối kỳ ({months} tháng)",
                "Tiền gốc": beginning_balance,
                "Tiền lãi kỳ này": total_interest,
                "Tổng tiền": balance
            })

    return pd.DataFrame(rows)


# ============================================================
# GIAO DIỆN
# ============================================================

st.title("💰 TÍNH LÃI SUẤT TIỀN GỬI TIẾT KIỆM")

st.markdown(
    """
    Ứng dụng hỗ trợ tính toán tiền gửi tiết kiệm theo **lãi đơn** 
    hoặc **lãi kép**, với nhiều hình thức nhận lãi.
    """
)

st.divider()

# ============================================================
# KHU VỰC NHẬP DỮ LIỆU
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("📌 Thông tin tiền gửi")

    principal = st.number_input(
        "Số tiền gửi (VNĐ)",
        min_value=100_000.0,
        value=100_000_000.0,
        step=1_000_000.0,
        format="%.0f"
    )

    months = st.number_input(
        "Kỳ hạn (tháng)",
        min_value=1,
        max_value=600,
        value=12,
        step=1
    )

    annual_rate = st.number_input(
        "Lãi suất (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.1,
        format="%.2f"
    )

with col2:

    st.subheader("⚙️ Hình thức tính")

    interest_type = st.radio(
        "Phương pháp tính lãi",
        [
            "Lãi đơn",
            "Lãi kép"
        ],
        horizontal=True
    )

    payment_method = st.selectbox(
        "Hình thức nhận lãi",
        [
            "Hàng tháng",
            "Hàng quý",
            "Cuối kỳ"
        ]
    )

    st.info(
        f"""
        **Thông tin đã chọn**

        - Tiền gửi: {format_money(principal)}
        - Kỳ hạn: {months} tháng
        - Lãi suất: {annual_rate:.2f}%/năm
        - Phương pháp: {interest_type}
        - Nhận lãi: {payment_method}
        """
    )

# ============================================================
# NÚT TÍNH TOÁN
# ============================================================

st.divider()

calculate_button = st.button(
    "🧮 TÍNH LÃI SUẤT",
    type="primary",
    use_container_width=True
)

if calculate_button:

    # Kiểm tra dữ liệu
    if principal <= 0:
        st.error("Số tiền gửi phải lớn hơn 0.")
        st.stop()

    if months <= 0:
        st.error("Kỳ hạn phải lớn hơn 0.")
        st.stop()

    if annual_rate < 0:
        st.error("Lãi suất không được âm.")
        st.stop()

    # Tính toán
    result = calculate_periodic_interest(
        principal=principal,
        annual_rate=annual_rate,
        months=months,
        interest_type=interest_type,
        payment_method=payment_method
    )

    total_interest = result["total_interest"]
    total_amount = result["total_amount"]
    periodic_interest = result["periodic_interest"]

    # ========================================================
    # KẾT QUẢ
    # ========================================================

    st.header("📊 KẾT QUẢ TÍNH TOÁN")

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:

        if periodic_interest is not None:
            periodic_display = format_money(periodic_interest)
        else:
            if payment_method == "Hàng tháng":
                periodic_display = "Tính theo số dư thực tế"
            elif payment_method == "Hàng quý":
                periodic_display = "Tính theo số dư thực tế"
            else:
                periodic_display = format_money(total_interest)

        st.metric(
            "💵 Tiền lãi định kỳ",
            periodic_display
        )

    with result_col2:

        st.metric(
            "📈 Tổng tiền lãi",
            format_money(total_interest)
        )

    with result_col3:

        st.metric(
            "💰 Tổng gốc + lãi",
            format_money(total_amount)
        )

    # ========================================================
    # THÔNG TIN CHI TIẾT
    # ========================================================

    st.subheader("📋 Thông tin chi tiết")

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:

        st.write("**Tiền gửi ban đầu:**")
        st.write(format_money(principal))

        st.write("**Lãi suất:**")
        st.write(f"{annual_rate:.2f}%/năm")

        st.write("**Kỳ hạn:**")
        st.write(f"{months} tháng")

    with detail_col2:

        st.write("**Phương pháp tính:**")
        st.write(interest_type)

        st.write("**Hình thức nhận lãi:**")
        st.write(payment_method)

        st.write("**Tổng tiền nhận:**")
        st.write(format_money(total_amount))

    # ========================================================
    # BẢNG LỊCH NHẬN LÃI
    # ========================================================

    st.subheader("📅 Lịch tính lãi")

    schedule = create_schedule(
        principal=principal,
        annual_rate=annual_rate,
        months=months,
        interest_type=interest_type,
        payment_method=payment_method
    )

    # Định dạng bảng để hiển thị
    display_schedule = schedule.copy()

    for column in [
        "Tiền gốc",
        "Tiền lãi kỳ này",
        "Tổng tiền"
    ]:
        display_schedule[column] = display_schedule[column].apply(
            lambda x: f"{x:,.0f} VNĐ".replace(",", ".")
        )

    st.dataframe(
        display_schedule,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # CÔNG THỨC
    # ========================================================

    with st.expander("📐 Xem công thức tính"):

        if interest_type == "Lãi đơn":

            st.markdown(
                """
                ### Lãi đơn

                **Tiền lãi:**

                `Tiền lãi = Tiền gốc × Lãi suất năm × Kỳ hạn / 12`

                **Tổng tiền nhận:**

                `Tổng tiền = Tiền gốc + Tiền lãi`

                Với hình thức lãi đơn, tiền lãi được tính dựa trên
                số tiền gốc ban đầu.
                """
            )

        else:

            st.markdown(
                """
                ### Lãi kép

                **Lãi suất tháng:**

                `Lãi suất tháng = Lãi suất năm / 12`

                **Tổng tiền cuối kỳ:**

                `Tổng tiền = Tiền gốc × (1 + Lãi suất tháng)^Số tháng`

                **Tổng tiền lãi:**

                `Tổng tiền lãi = Tổng tiền - Tiền gốc`

                Với lãi kép, tiền lãi phát sinh được cộng vào số dư
                và tiếp tục được tính lãi ở các kỳ tiếp theo.
                """
            )

    # ========================================================
    # GHI CHÚ
    # ========================================================

    st.warning(
        """
        **Lưu ý:** Đây là công cụ mô phỏng theo công thức toán học.
        Lãi suất thực tế của ngân hàng có thể áp dụng quy định riêng
        về ngày tính lãi, số ngày trong năm, tất toán trước hạn,
        phương thức trả lãi và các điều kiện của từng sản phẩm tiền gửi.
        """
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "💰 Ứng dụng tính lãi suất tiền gửi tiết kiệm | "
    "Xây dựng bằng Streamlit"
)
