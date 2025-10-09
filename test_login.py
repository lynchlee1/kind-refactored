#!/usr/bin/env python3

from designlib.ui_components import create_simple_login_page

# Generate the login page HTML
login_html = create_simple_login_page()

# Save it to a file so you can open it in your browser
with open('login_page.html', 'w', encoding='utf-8') as f:
    f.write(login_html)

print("Login page HTML generated and saved to 'login_page.html'")
print("Open this file in your browser to see the login page!")
print("\nThe login page includes:")
print("- Header with '로그인' title and '시스템에 접속하세요' subtitle")
print("- Username input field")
print("- Password input field") 
print("- Login button (submit)")
print("- Cancel button (goes back)")
print("- Form validation JavaScript")
