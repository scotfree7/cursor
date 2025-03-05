import re

def debug_analyze_question(question):
    """Debug version of analyze_question method"""
    print(f"Original question: {question}")
    
    # Lowercase for analysis
    question = question.lower()
    print(f"Lowercase question: {question}")
    
    # Check for options queries and personal queries
    is_options_query = re.search(r'\b(option|call|put)\b', question)
    is_personal = re.search(r'\b(my|i\s+have|i\s+own|i\s+bought|i\s+purchased|bought\s+a|will\s+it|will\s+my)\b', question)
    personal_option_query = is_options_query and is_personal
    
    print(f"Is options query: {bool(is_options_query)}")
    print(f"Is personal query: {bool(is_personal)}")
    print(f"Is personal option query: {bool(personal_option_query)}")
    
    found_symbols = []
    
    # Define company name to ticker mapping
    company_to_ticker = {
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'amazon': 'AMZN',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'facebook': 'META',
        'meta': 'META',
        'tesla': 'TSLA',
        'nvidia': 'NVDA',
        'netflix': 'NFLX'
    }
    
    # Common tickers to search for
    common_tickers = ['aapl', 'msft', 'amzn', 'googl', 'goog', 'meta', 'tsla', 'nvda', 'nflx', 'dis']
    
    # Common words to exclude from stock symbol matching
    exclude_words = ['a', 'i', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
                     'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
                     'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
                     'both', 'each', 'few', 'more', 'most', 'some', 'such', 'no', 'nor', 'not',
                     'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
                     'just', 'don', 'should', 'now', 'my', 'with', 'for', 'by', 'from', 'get',
                     'have', 'has', 'had', 'did', 'do', 'does', 'is', 'are', 'am', 'was', 'were',
                     'be', 'been', 'being', 'call', 'put', 'option', 'stock', 'price', 'mar', 'apr',
                     'jan', 'feb', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'next', 'last',
                     'year', 'month', 'week', 'day', 'that', 'this', 'these', 'those', 'what', 'which']
    
    # For all option queries (personal or not), prioritize company names over everything else
    if is_options_query:
        print("Processing options query - checking for company names first")
        # First try to match company names in option queries
        for company, ticker in company_to_ticker.items():
            pattern = r'\b' + re.escape(company) + r'\b'
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                print(f"Found company match: {company} -> {ticker}")
                found_symbols = [ticker]  # Replace any previously found symbols
                break  # Only need one match for options
        
        # If no company name found, look for common ticker symbols
        if not found_symbols:
            print("No company name found, checking for common ticker symbols")
            for ticker in common_tickers:
                pattern = r'\b' + ticker + r'\b'
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    print(f"Found ticker match: {ticker.upper()}")
                    found_symbols = [ticker.upper()]  # Replace any previously found symbols
                    break  # Only need one match for options
        
        # If still no symbols found, it's likely not a valid option query
        if not found_symbols and personal_option_query:
            print("No stock symbol identified in option query")
            return "ERROR: Could not identify stock symbol"
    else:
        print("Not an options query - using standard approach")
        # Standard approach for non-options queries...
    
    # If we found symbols, use them
    if found_symbols:
        print(f"Final symbols found: {found_symbols}")
        return found_symbols
    else:
        print("No symbols found")
        return "ERROR: No symbols found"

# Test with the question
test_question = "i bought a tesla call at strike 440 that expires on mar 21 next year, will it make money?"
result = debug_analyze_question(test_question)
print("\nFinal result:", result) 