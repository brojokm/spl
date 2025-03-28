def format_currency(amount):
    """Format amount in Indian currency format (Lakhs and Crores)"""
    if amount >= 10000000:  # 1 Crore = 10,000,000
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 Lakh = 100,000
        return f"₹{amount/100000:.2f} Lakh"
    else:
        return f"₹{amount:,}" 