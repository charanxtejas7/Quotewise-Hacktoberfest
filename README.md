# Quotewise

Quotewise is an open-source quotation comparison application built with Python, Streamlit, and Sarvam AI.

It helps people compare service-provider quotations, calculate price differences, identify items appearing in only one quotation, and understand results in Indian languages.

## Problem Statement

Comparing quotations from plumbers, electricians, mechanics, and other service providers can be difficult. Different quotations may contain different items, prices, and service charges, making informed decisions harder.

## Solution

Quotewise provides a simple interface for entering two quotations and comparing their totals and individual line items.

Sarvam AI helps make quotation comparisons more accessible through explanations in supported Indian languages.

## Features

- **Quotation comparison:** Calculate totals and item-level price differences.
- **Missing-item detection:** Identify items listed in only one quotation.
- **Multilingual explanations:** Use Sarvam AI to explain comparison results.
- **CSV export:** Download a comparison report for later reference.
- **Input validation:** Reject invalid quantities, negative prices, and incorrectly formatted entries.

## Technology Stack

- Python
- Streamlit
- Pandas
- Sarvam AI
- python-dotenv

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/charanxtejas7/Quotewise-Hacktoberfest.git
cd Quotewise-Hacktoberfest
