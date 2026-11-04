#!/usr/bin/env python3

# Read homepage
with open('/var/www/aiwave/aiwave/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update plan names in pricing section
content = content.replace('color-var-two">Premium<', 'color-var-two">Standard<')
content = content.replace('color-var-three">Enterprise<', 'color-var-three">Premium<')

# Update buttons in pricing section to rainbow-gradient-btn
content = content.replace('class="btn-default" style="background: #7c3aed !important; background-image: none !important;"', 'class="rainbow-gradient-btn"')
content = content.replace('class="btn-default color-blacked"', 'class="rainbow-gradient-btn"')

# Make sure buttons have span inside
content = content.replace('<a class="rainbow-gradient-btn" href="/signup/">Get Started</a>', '<a class="rainbow-gradient-btn" href="/signup/"><span>Get Started</span></a>')

# Update trial text to be consistent (capitalize Day)
content = content.replace('7-day free trial', '7-Day Free Trial')

# Write back
with open('/var/www/aiwave/aiwave/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Homepage pricing section updated successfully!')
print('- Plan names: Basic, Standard, Premium')
print('- Buttons: rainbow-gradient-btn with span')
print('- Trial text: 7-Day Free Trial')
