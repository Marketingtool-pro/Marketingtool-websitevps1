#!/usr/bin/env python3

# Read and normalize line endings
with open('/var/www/aiwave/aiwave/templates/pages/pricing.html.bak', 'rb') as f:
    content = f.read().decode('utf-8')

# Normalize line endings
content = content.replace('\r\n', '\n').replace('\r', '\n')

# Update buttons
content = content.replace('class="btn-default" style="background: #7c3aed !important; background-image: none !important;"', 'class="rainbow-gradient-btn"')
content = content.replace('<a class="rainbow-gradient-btn" href="/signup/">Get Started</a>', '<a class="rainbow-gradient-btn" href="/signup/"><span>Get Started</span></a>')

# Update plan names
content = content.replace('color-var-two">Premium<', 'color-var-two">Standard<')
content = content.replace('color-var-three">Enterprise<', 'color-var-three">Premium<')

# Update trial text
content = content.replace('Limited Offer', '7-Day Free Trial')

# Monthly prices
content = content.replace('<span class="price-text">Free</span>', '<span class="price-text">TEMP_BASIC_MONTHLY</span>', 1)
content = content.replace('<span class="price-text">$60.50</span>', '<span class="price-text">$9</span>')
content = content.replace('<span class="price-text">$80.50</span>', '<span class="price-text">$16</span>')

# Yearly prices
content = content.replace('<span class="price-text">Free</span>', '<span class="price-text">$49</span>', 1)
content = content.replace('<span class="price-text">$499.00</span>', '<span class="price-text">$99</span>')
content = content.replace('<span class="price-text">$599.00</span>', '<span class="price-text">$499</span>')

# Replace placeholder
content = content.replace('TEMP_BASIC_MONTHLY', '$3')

# Write output
with open('/var/www/aiwave/aiwave/templates/pages/pricing.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Pricing page updated successfully!')
print('- Monthly: Basic $3, Standard $9, Premium $16')
print('- Yearly: Basic $49, Standard $99, Premium $499')
print('- Buttons updated to rainbow-gradient-btn')
print('- Plan names updated')
print('- Trial text updated')
