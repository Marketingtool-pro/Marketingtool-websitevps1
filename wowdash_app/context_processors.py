from wowdash_app.models import ContentSetting
from django.conf import settings
import logging
from Dal.wowdash_app.siteMetaSettings import get_all_site_settings

logger = logging.getLogger(__name__)

# SEO meta descriptions by URL path
SEO_DESCRIPTIONS = {
    '/': 'MarketingTool is an AI Marketing Operating System for Google & Meta Ads. Automate campaigns, optimize performance, and scale profitably with 8 AI models.',
    '/pricing/': 'MarketingTool pricing: Starter $29/mo, Pro $59/mo, Growth $99/mo and custom Agency plans, all with a 7-day free trial. AI automation for Google and Meta Ads.',
    '/about/': 'MarketingTool is an AI-powered marketing platform for performance marketers who automate Google Ads, Meta Ads, and SEO with 8 models to scale profitably.',
    '/contact/': 'Contact MarketingTool support for AI marketing campaigns, ad automation, integrations, billing questions, and partnership inquiries. Reply within 24 hours.',
    '/blog/': 'MarketingTool blog: expert guides on AI marketing, Google Ads, Meta Ads, SEO, creative automation, conversion optimization, and campaign management in 2026.',
    '/free-tools/': 'Free AI marketing tools from MarketingTool: Google Ads grader, Facebook Ads auditor, website SEO checker, and keyword analyzer — instant reports, no signup.',
    '/free-tools/google-ads/': 'Free Google Ads audit tool. Find wasted spend, audit Quality Scores, spot conversion tracking issues, and get AI optimization tips in 60 seconds.',
    '/free-tools/facebook-ads/': 'Free Facebook Ads audit tool. Analyze Meta campaigns, track ROAS by creative, find underperforming audiences, and get AI recommendations to improve results.',
    '/free-tools/website/': 'Free website audit tool. Check SEO issues, Core Web Vitals, mobile experience, performance bottlenecks, and conversion optimization opportunities instantly.',
    '/how-to-use/': 'Learn to use MarketingTool: automate campaigns with AI. Step-by-step setup, Google Ads and Meta Ads integration, SEO workflows, and best practice tips.',
    '/guide/': 'Complete MarketingTool guide: campaign automation, AI creative generation, analytics, multi-platform ad management, SEO workflows, and reporting for teams.',
    '/roadmap/': 'MarketingTool product roadmap 2026: AI model upgrades, new ad integrations, enhanced analytics, Google and Meta automation, and platform performance goals.',
    '/audit-report/': 'Get a comprehensive AI-powered audit report for your Google & Meta ad accounts. Identify wasted spend, find growth opportunities, and fix conversion gaps.',
    '/help/': 'MarketingTool help center: answers for campaigns, billing, integrations, AI tools, setup guides, troubleshooting, and account management — browse FAQs now.',
    '/team/': 'Meet the MarketingTool team building the future of AI-powered marketing automation for performance marketers scaling Google & Meta Ads in 2026.',
    '/release-notes/': 'MarketingTool release notes and changelog: latest feature updates, bug fixes, AI model upgrades, UI improvements, and platform performance changes by date.',
    '/privacy-policy/': 'MarketingTool privacy policy: learn how we collect, use, store, and protect your data, including GDPR compliance, cookies, and user rights under data law.',
    '/terms-policy/': 'MarketingTool terms and conditions: read our terms of service for using the AI marketing platform, subscription plans, user responsibilities, and liability.',
    '/cookie-policy/': 'MarketingTool cookie policy: learn about the cookies we use, how they track usage, and how to manage your preferences for privacy and website functionality.',
    '/trust-verification/': 'MarketingTool trust and verification: security practices, data protection, SOC compliance, Meta reviews, and Google partnership credentials in one place.',
    '/refund-policy/': 'MarketingTool refund policy: 14-day money back guarantee on all paid plans, cancellation terms, pro-rated refunds, and eligibility criteria for returns.',
    '/delete-account/': 'Delete your MarketingTool account. Learn how to remove your data, close your subscription, cancel billing, and export your information first.',
    '/signup/': 'Sign up for MarketingTool free trial. Automate Google Ads, Meta Ads, and SEO with 8 AI models. 7-day trial, no credit card required, cancel anytime online.',
    '/signin/': 'Sign in to MarketingTool. Access your AI marketing dashboard: Google Ads and Meta Ads campaigns, ad accounts, analytics, automations, and daily reports.',

    '/keywords-search-terms/': 'AI-powered keyword research and search terms analysis. Find high-converting keywords, filter by intent, and optimize Google and Meta campaigns profitably.',
    # Tools
    '/tools/ai-marketing-agents/': 'AI Marketing Agents automate Google Ads and Meta Ads 24/7: bid optimization, creative generation, budget management, and performance reporting.',
    '/tools/ecommerce-shopify/': 'AI e-commerce and Shopify marketing tools: automate product descriptions, ad creative, campaign optimization, and abandoned cart flows for online stores.',
    '/tools/analytics/': 'AI-powered marketing analytics platform: real-time dashboards, multi-channel attribution, predictive insights, and automated reports for performance teams.',
    '/tools/content-writing/': 'AI content writing tools for marketers: generate blog posts, ad copy, email campaigns, product descriptions, and landing page headlines with 8 AI models.',
    '/tools/creative-ads/': 'AI creative and ads tools: generate high-converting ad copy, images, and video scripts. A/B test creative variations at scale across Google and Meta Ads.',
    '/tools/seo/': 'AI SEO tools for marketers: technical audits, keyword research, content optimization, schema markup generation, and on-page improvements for higher rankings.',
    '/tools/ppc-optimization/': 'AI PPC optimization tools by MarketingTool: automate bid management, reduce wasted spend, maximize ROAS, and scale profitably on Google Ads and Meta Ads.',
    # Resources
    '/resources/creative-ads/': 'Creative & Ads resources. Learn how AI generates high-converting ad creative, headlines, and visual content.',
    '/resources/ai-agents/': 'AI Marketing Agents resources. Understand how autonomous agents manage and optimize your ad campaigns.',
    '/resources/analytics/': 'Analytics platform resources. Learn about AI-powered dashboards, attribution models, and performance tracking.',
    '/resources/automation/': 'Marketing automation resources. Discover how AI automates campaign workflows, bidding, and reporting.',
    '/resources/audit-tools/': 'Audit tools resources. Learn how AI audits identify wasted ad spend and growth opportunities.',
    '/resources/campaign-hub/': 'Multi-platform campaign hub resources. Manage Google, Meta, and other ad platforms from one dashboard.',
    '/resources/campaign-management/': 'Campaign management resources. Best practices for creating, optimizing, and scaling ad campaigns with AI.',
    '/resources/agentic-marketing/': 'Agentic marketing resources. Explore how AI agents autonomously manage marketing operations.',
    '/resources/creative-intelligence/': 'Creative intelligence resources. Learn how AI analyzes ad creative performance and generates winning variations.',
    '/resources/content-writing/': 'Content writing resources. Discover AI tools for blog writing, email copy, and product descriptions.',
    '/resources/management-tools/': 'Management tools resources. Overview of AI-powered tools for marketing team productivity and collaboration.',
    '/resources/ppc-research/': 'PPC research resources. AI-powered competitive analysis, keyword research, and market intelligence for paid search.',
    '/resources/ppc-audit/': 'PPC audit resources. Learn how AI audits find hidden waste and unlock growth in your ad accounts.',
    '/resources/test-drive/': 'Test drive MarketingTool dashboard. See how AI-powered analytics and campaign management work in action.',
    # Solutions
    '/solutions/email-campaign/': 'AI email campaign automation. Generate subject lines, body copy, and optimize send times for maximum engagement.',
    '/solutions/website-generator/': 'AI website and landing page generator. Create high-converting pages optimized for SEO and paid traffic.',
    '/solutions/facebook-ads/': 'AI Meta/Facebook Ads automation. Automate campaign creation, audience targeting, and creative optimization.',
    '/solutions/campaign-builder/': 'AI campaign builder. Create multi-platform ad campaigns with AI-generated copy, targeting, and budget allocation.',
    '/solutions/summary-generator/': 'AI summary generator for marketers. Create executive summaries, reports, and briefs from your marketing data.',
    '/solutions/description-generator/': 'AI product description generator. Create compelling product copy for e-commerce, ads, and landing pages.',
}


def seo_page_description(request):
    """Auto-inject page_description based on URL path if not already set."""
    path = request.path
    desc = SEO_DESCRIPTIONS.get(path, '')
    return {'auto_page_description': desc}

def site_image(request):
    try:
        chat_bot_img = ContentSetting.objects.filter(key="chat_bot_image").first()
    except Exception:
        chat_bot_img = None

    return {
        'bot_image': chat_bot_img
    }

# New context processor for site meta settings

def site_meta_vars(request):
    """
    Provides meta_vars for site meta settings pages (contact info, file upload, general site, social media, access/security)
    Uses existing DAL function for efficiency
    """
    try:
        # Use existing DAL function to get all settings
        all_settings = get_all_site_settings()
        
        # Define the keys we want to expose
        keys = [
            'company_address', 'contact_email', 'contact_phone',
            'allowed_file_types', 'max_file_size',
            'site_name', 'site_description', 'site_logo', 'favicon_png', 'small_logo',
            'social_facebook', 'social_linkedin', 'social_twitter',
        ]
        
        # Create settings dict with defaults
        settings_dict = {k: all_settings.get(k, None) for k in keys}
        
        # Map the database keys to template-friendly names
        settings_dict['site_img'] = settings_dict.get('site_logo', '')
        settings_dict['favicon_logo'] = settings_dict.get('favicon_png', '')
        settings_dict['small_logo'] = settings_dict.get('small_logo', '')
        
        return {'meta_vars': settings_dict}
        
    except Exception as e:
        logger.error(f"Error in site_meta_vars context processor: {e}")
        # Return empty dict on error to prevent template errors
        return {'meta_vars': {}}