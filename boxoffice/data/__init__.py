# -*- coding: utf-8 -*-

indian_states = [
    {'short_code': 1, 'name': 'Jammu and Kashmir', 'short_code_text': 'JK'},
    {'short_code': 2, 'name': 'Himachal Pradesh', 'short_code_text': 'HP'},
    {'short_code': 3, 'name': 'Punjab', 'short_code_text': 'PB'},
    {'short_code': 4, 'name': 'Chandigarh', 'short_code_text': 'CH'},
    {'short_code': 5, 'name': 'Uttarakhand', 'short_code_text': 'UT'},
    {'short_code': 6, 'name': 'Haryana', 'short_code_text': 'HR'},
    {'short_code': 7, 'name': 'Delhi', 'short_code_text': 'DL'},
    {'short_code': 8, 'name': 'Rajasthan', 'short_code_text': 'RJ'},
    {'short_code': 9, 'name': 'Uttar Pradesh', 'short_code_text': 'UP'},
    {'short_code': 10, 'name': 'Bihar', 'short_code_text': 'BR'},
    {'short_code': 11, 'name': 'Sikkim', 'short_code_text': 'SK'},
    {'short_code': 12, 'name': 'Arunachal Pradesh', 'short_code_text': 'AR'},
    {'short_code': 13, 'name': 'Nagaland', 'short_code_text': 'NL'},
    {'short_code': 14, 'name': 'Manipur', 'short_code_text': 'MN'},
    {'short_code': 15, 'name': 'Mizoram', 'short_code_text': 'MZ'},
    {'short_code': 16, 'name': 'Tripura', 'short_code_text': 'TR'},
    {'short_code': 17, 'name': 'Meghalaya', 'short_code_text': 'ML'},
    {'short_code': 18, 'name': 'Assam', 'short_code_text': 'AS'},
    {'short_code': 19, 'name': 'West Bengal', 'short_code_text': 'WB'},
    {'short_code': 20, 'name': 'Jharkhand', 'short_code_text': 'JH'},
    {'short_code': 21, 'name': 'Odisha', 'short_code_text': 'OR'},
    {'short_code': 22, 'name': 'Chhattisgarh', 'short_code_text': 'CT'},
    {'short_code': 23, 'name': 'Madhya Pradesh', 'short_code_text': 'MP'},
    {'short_code': 24, 'name': 'Gujarat', 'short_code_text': 'GJ'},
    {'short_code': 25, 'name': 'Daman and Diu', 'short_code_text': 'DD'},
    {'short_code': 26, 'name': 'Dadra and Nagar Haveli', 'short_code_text': 'DN'},
    {'short_code': 27, 'name': 'Maharashtra', 'short_code_text': 'MH'},
    {'short_code': 28, 'name': 'Andhra Pradesh', 'short_code_text': 'AP'},
    {'short_code': 29, 'name': 'Karnataka', 'short_code_text': 'KA'},
    {'short_code': 30, 'name': 'Goa', 'short_code_text': 'GA'},
    {'short_code': 31, 'name': 'Lakshadweep', 'short_code_text': 'LD'},
    {'short_code': 32, 'name': 'Kerala', 'short_code_text': 'KL'},
    {'short_code': 33, 'name': 'Tamil Nadu', 'short_code_text': 'TN'},
    {'short_code': 34, 'name': 'Puducherry', 'short_code_text': 'PY'},
    {'short_code': 35, 'name': 'Andaman and Nicobar Islands', 'short_code_text': 'AN'},
    {'short_code': 36, 'name': 'Telangana', 'short_code_text': 'TG'},
    {'short_code': 37, 'name': 'Andhra Pradesh (New)', 'short_code_text': 'AD'}
    ]

indian_states_dict = dict((d["short_code_text"], d) for d in indian_states)

short_codes = [state['short_code'] for state in indian_states]
