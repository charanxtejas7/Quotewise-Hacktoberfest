import csv
import io
import streamlit as st

from quote_engine import compare_quotes
from sarvam_helper import explain_quote


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Quotewise",
    page_icon="🧾",
    layout="wide",
)

st.title("🧾 Quotewise")
st.caption(
    "Compare service quotations, identify missing items, "
    "and understand price differences with AI-powered explanations."
)

st.markdown(
    """
    Enter two service quotations to compare their prices, identify items
    appearing in only one quotation, and make a more informed decision.
    """
)


# ---------------- SAMPLE QUOTATIONS ----------------

SAMPLE_QUOTE_A = """Labour,1,1800
Pipe replacement,1,2250
Materials,1,1500
Inspection,1,1300"""

SAMPLE_QUOTE_B = """Labour,1,1700
Pipe replacement,1,2300
Materials,1,1650
Transportation,1,1200"""


# ---------------- QUOTATION PARSING ----------------

def parse_quote(text: str) -> list[dict]:
    """Parse and validate lines formatted as: item name, quantity, unit price."""
    if not text.strip():
        raise ValueError("Please enter at least one quotation item.")

    items = []

    try:
        reader = csv.reader(io.StringIO(text.strip()))

        for line_number, row in enumerate(reader, start=1):
            if not row or all(not value.strip() for value in row):
                continue

            if len(row) != 3:
                raise ValueError(
                    f"Line {line_number}: Enter exactly three values — "
                    "item name, quantity, and unit price."
                )

            name = row[0].strip()
            if not name:
                raise ValueError(f"Line {line_number}: Item name cannot be empty.")

            try:
                quantity = float(row[1].strip())
                unit_price = float(row[2].strip())
            except ValueError:
                raise ValueError(
                    f"Line {line_number}: Quantity and unit price must be numbers."
                )

            if quantity <= 0:
                raise ValueError(
                    f"Line {line_number}: Quantity must be greater than zero."
                )
            if unit_price < 0:
                raise ValueError(
                    f"Line {line_number}: Unit price cannot be negative."
                )

            items.append(
                {
                    "name": name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                }
            )

    except csv.Error as error:
        raise ValueError("Unable to read the quotation. Check its formatting.") from error

    if not items:
        raise ValueError("Please enter at least one valid quotation item.")

    return items


# ---------------- QUOTATION INPUT ----------------

st.subheader("1. Enter your quotations")
st.info(
    "Use one item per line in this format: Item name, quantity, unit price. "
    "Example: Labour, 1, 800. Prices below are illustrative."
)

left, right = st.columns(2)

with left:
    st.markdown("### 📄 Quotation A")
    quote_a_text = st.text_area(
        "Enter quotation A",
        value=SAMPLE_QUOTE_A,
        height=190,
        help="Format: Item name, quantity, unit price. One item per line.",
        key="quote_a_text",
    )

with right:
    st.markdown("### 📄 Quotation B")
    quote_b_text = st.text_area(
        "Enter quotation B",
        value=SAMPLE_QUOTE_B,
        height=190,
        help="Format: Item name, quantity, unit price. One item per line.",
        key="quote_b_text",
    )

compare_button = st.button(
    "Compare Quotations",
    type="primary",
    use_container_width=True,
)

if compare_button:
    try:
        items_a = parse_quote(quote_a_text)
        items_b = parse_quote(quote_b_text)
        st.session_state["comparison_result"] = compare_quotes(items_a, items_b)
        st.session_state.pop("comparison_error", None)
    except (ValueError, KeyError, TypeError) as error:
        st.session_state["comparison_error"] = str(error)
        st.session_state.pop("comparison_result", None)
    except Exception as error:
        st.session_state["comparison_error"] = (
            f"Comparison failed: {type(error).__name__}: {error}"
        )
        st.session_state.pop("comparison_result", None)

if st.session_state.get("comparison_error"):
    st.error(st.session_state["comparison_error"])


# ---------------- COMPARISON RESULTS ----------------

result = st.session_state.get("comparison_result")

if result:
    st.divider()
    st.header("2. Comparison results")

    metric_a, metric_b, metric_difference = st.columns(3)

    with metric_a:
        st.metric("Quotation A total", f"₹{result['total_a']:,.2f}")

    with metric_b:
        st.metric("Quotation B total", f"₹{result['total_b']:,.2f}")

    difference = result["difference"]
    with metric_difference:
        st.metric(
            "Difference (B − A)",
            f"₹{abs(difference):,.2f}",
            delta=(
                f"Quote B costs ₹{difference:,.2f} more"
                if difference > 0
                else f"Quote B costs ₹{abs(difference):,.2f} less"
                if difference < 0
                else "Both totals are equal"
            ),
            delta_color="inverse",
        )

    if result["cheaper_quote"] == "Same total":
        st.info("Both quotations have the same total price.")
    else:
        cheaper_total = (
            result["total_a"]
            if result["cheaper_quote"] == "Quote A"
            else result["total_b"]
        )
        higher_total = max(result["total_a"], result["total_b"])
        st.success(
            f"**{result['cheaper_quote']} has the lower total** — "
            f"₹{higher_total - cheaper_total:,.2f} less."
        )

    st.subheader("Item-by-item comparison")
    st.caption(
        "Item costs are calculated as quantity × unit price. "
        "Items with similar but differently written names may be treated separately."
    )

    st.dataframe(
        result["items"],
        use_container_width=True,
        hide_index=True,
        column_config={
            "item": st.column_config.TextColumn("Item"),
            "quote_a": st.column_config.NumberColumn("Quote A (₹)", format="₹%.2f"),
            "quote_b": st.column_config.NumberColumn("Quote B (₹)", format="₹%.2f"),
            "difference": st.column_config.NumberColumn(
                "Difference (B − A) (₹)", format="₹%.2f"
            ),
            "status": st.column_config.TextColumn("Availability"),
        },
    )

    st.subheader("3. Missing-item detection")
    only_a = [
        item["item"]
        for item in result["items"]
        if item["status"] == "Only in Quote A"
    ]
    only_b = [
        item["item"]
        for item in result["items"]
        if item["status"] == "Only in Quote B"
    ]

    missing_left, missing_right = st.columns(2)

    with missing_left:
        st.markdown("**Items absent from Quotation B**")
        if only_a:
            for item in only_a:
                st.warning(item)
        else:
            st.write("No unique items found in Quotation A.")

    with missing_right:
        st.markdown("**Items absent from Quotation A**")
        if only_b:
            for item in only_b:
                st.warning(item)
        else:
            st.write("No unique items found in Quotation B.")

    st.caption(
        "An item appearing in only one quotation is not automatically an omission. "
        "Confirm the scope of work, parts, warranty, and taxes with each provider."
    )

    # Downloadable CSV comparison report
    report_buffer = io.StringIO()
    writer = csv.writer(report_buffer)
    writer.writerow(
        ["Item", "Quote A (INR)", "Quote B (INR)", "Difference (B - A)", "Availability"]
    )

    for item in result["items"]:
        writer.writerow(
            [
                item["item"],
                item["quote_a"],
                item["quote_b"],
                item["difference"],
                item["status"],
            ]
        )

    writer.writerow([])
    writer.writerow(["Total Quote A", result["total_a"]])
    writer.writerow(["Total Quote B", result["total_b"]])
    writer.writerow(["Difference (B - A)", result["difference"]])
    writer.writerow(["Lower total", result["cheaper_quote"]])

    st.download_button(
        "Download comparison report (CSV)",
        data=report_buffer.getvalue(),
        file_name="quotewise_comparison.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.divider()
    st.subheader("How to use Quotewise")
    st.markdown(
        """
        1. Enter the items from your first quotation.
        2. Enter the items from your second quotation.
        3. Select **Compare Quotations**.
        4. Review the totals, item-level differences, and missing items.
        5. Download the comparison as a CSV report.
        """
    )


# ---------------- SARVAM AI EXPLANATION ----------------

st.divider()
st.header("🌐 4. Understand your quotations with Sarvam AI")
st.write(
    "Get a simpler explanation of the comparison in an Indian language. "
    "The quote calculations work independently of the AI service."
)

language = st.selectbox(
    "Choose your explanation language",
    ["English", "Kannada", "Hindi", "Tamil", "Telugu"],
    key="explanation_language",
)

if st.button("Explain with Sarvam AI", type="primary", use_container_width=True):
    current_result = st.session_state.get("comparison_result")

    if not current_result:
        st.warning("Compare the quotations first.")
    else:
        language_names = {
            "English": "English",
            "Kannada": "Kannada",
            "Hindi": "Hindi",
            "Tamil": "Tamil",
            "Telugu": "Telugu",
        }

        summary = (
            f"Quotation A total: ₹{current_result['total_a']:.2f}. "
            f"Quotation B total: ₹{current_result['total_b']:.2f}. "
            f"Difference (B minus A): ₹{current_result['difference']:.2f}. "
            f"Lower total: {current_result['cheaper_quote']}. "
            f"Items only in Quote A: {', '.join(only_a) if current_result is result and 'only_a' in locals() else 'Review the comparison table'}. "
            f"Items only in Quote B: {', '.join(only_b) if current_result is result and 'only_b' in locals() else 'Review the comparison table'}. "
            "Explain the results clearly. Do not invent facts. Mention that the lowest "
            "price does not automatically mean the best quality, and recommend checking "
            "scope of work, parts, warranty, and taxes."
        )

        with st.spinner("Preparing your explanation..."):
            explanation = explain_quote(summary, language_names[language])

        st.markdown(explanation)


st.divider()
st.caption("Quotewise · Open source · Python · Streamlit · Sarvam AI")
