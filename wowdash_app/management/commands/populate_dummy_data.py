from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal, ROUND_DOWN
from faker import Faker
from ...models import (
    UserProfile, UserActivity, Blog, TeamMember, ReleaseNote,
    UserSession, UserQueries, FAQ, ChatSession, ChatMessage,
    Subscription, GeneratedContent, EnvVar, ContentSetting
)
from django.utils.text import slugify

fake = Faker()

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Starting to populate dummy data...'))
        
        # Keep track of created users
        users = []
        
        # Define realistic departments and their corresponding designations
        DEPARTMENTS = {
            'Engineering': [
                'Software Engineer',
                'Senior Software Engineer',
                'Lead Engineer',
                'Engineering Manager',
                'QA Engineer',
                'DevOps Engineer',
                'System Architect',
                'Full Stack Developer',
                'Backend Developer',
                'Frontend Developer'
            ],
            'Product': [
                'Product Manager',
                'Senior Product Manager',
                'Product Owner',
                'Product Analyst',
                'Product Designer',
                'Product Marketing Manager',
                'Technical Product Manager'
            ],
            'Design': [
                'UI Designer',
                'UX Designer',
                'Senior Designer',
                'Creative Director',
                'Graphic Designer',
                'Visual Designer',
                'Interaction Designer',
                'Motion Designer'
            ],
            'Marketing': [
                'Marketing Manager',
                'Digital Marketing Specialist',
                'Content Writer',
                'SEO Specialist',
                'Social Media Manager',
                'Brand Manager',
                'Marketing Analyst',
                'Growth Hacker'
            ],
            'Sales': [
                'Sales Representative',
                'Sales Manager',
                'Account Executive',
                'Business Development Manager',
                'Sales Operations Manager',
                'Customer Success Manager',
                'Sales Engineer'
            ],
            'Human Resources': [
                'HR Manager',
                'HR Specialist',
                'Recruiter',
                'Talent Acquisition Specialist',
                'HR Business Partner',
                'Learning & Development Manager',
                'Compensation & Benefits Manager'
            ],
            'Finance': [
                'Financial Analyst',
                'Accountant',
                'Finance Manager',
                'Controller',
                'Financial Planning Analyst',
                'Investment Analyst',
                'Treasury Manager'
            ],
            'Customer Support': [
                'Support Specialist',
                'Customer Success Manager',
                'Technical Support Engineer',
                'Support Team Lead',
                'Customer Experience Manager',
                'Client Success Specialist'
            ],
            'Data Science': [
                'Data Scientist',
                'Machine Learning Engineer',
                'Data Analyst',
                'Business Intelligence Analyst',
                'Data Engineer',
                'AI Research Scientist'
            ],
            'Operations': [
                'Operations Manager',
                'Supply Chain Manager',
                'Logistics Coordinator',
                'Process Improvement Specialist',
                'Operations Analyst',
                'Project Manager'
            ]
        }

        # Bot modes
        BOT_MODES = [
            'email-generator',
            'summary-generator',
            'code-generator',
            'description-generator',
            'blog-generator',
            'text-generator'
        ]

        self.stdout.write(self.style.SUCCESS('👥 Creating users and their profiles...'))
        # Create regular users (excluding superuser)
        for i in range(50):
            # Generate realistic name
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            # Generate realistic email based on name
            email_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com', 'tech.com']
            email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(email_domains)}"
            
            # Create user
            user = User.objects.create_user(
                username=email.split('@')[0],  # Use email username as username
                email=email,
                password='testuser@123',
                first_name=first_name,
                last_name=last_name
            )
            users.append(user)
            
            # Select random department and designation
            department = random.choice(list(DEPARTMENTS.keys()))
            designation = random.choice(DEPARTMENTS[department])
            
            # Create or get user profile with realistic data
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'user',
                    'profile_picture': 'assets/images/users/user1.png',
                    'is_active': random.choice([True, True, True, False]),  # 75% active
                    'department': department,
                    'designation': designation
                }
            )
            
            # If profile already existed, update department and designation
            if not created:
                profile.department = department
                profile.designation = designation
                profile.save()
            
            # Create user activity with realistic timestamps
            last_login = timezone.now() - timedelta(days=random.randint(0, 30))
            UserActivity.objects.create(
                user=user,
                last_login_time=last_login,
                last_logout_time=last_login + timedelta(minutes=random.randint(30, 480)),
                session_duration=timedelta(minutes=random.randint(30, 480))
            )
            if (i + 1) % 10 == 0:
                self.stdout.write(self.style.SUCCESS(f'✅ Created {i + 1} users with profiles and activities'))
                departments = set(u.profile.department for u in users[-10:] if u.profile.department)
                designations = set(u.profile.designation for u in users[-10:] if u.profile.designation)
                if departments:
                    self.stdout.write(self.style.SUCCESS(f'📊 Department distribution: {", ".join(departments)}'))
                if designations:
                    self.stdout.write(self.style.SUCCESS(f'👔 Designation distribution: {", ".join(designations)}'))

        # Track department and designation statistics
        department_stats = {}
        designation_stats = {}
        for user in users:
            dept = user.profile.department
            desig = user.profile.designation
            if dept:
                department_stats[dept] = department_stats.get(dept, 0) + 1
            if desig:
                designation_stats[desig] = designation_stats.get(desig, 0) + 1

        if department_stats:
            self.stdout.write(self.style.SUCCESS('\n📊 Department Statistics:'))
            for dept, count in department_stats.items():
                self.stdout.write(self.style.SUCCESS(f'  • {dept}: {count} users'))

        if designation_stats:
            self.stdout.write(self.style.SUCCESS('\n👔 Designation Statistics:'))
            for desig, count in designation_stats.items():
                self.stdout.write(self.style.SUCCESS(f'  • {desig}: {count} users'))

        self.stdout.write(self.style.SUCCESS('\n💳 Creating subscription plans...'))
        # Create subscriptions with realistic plans and pricing
        subscription_plans = [
            {'name': 'Basic', 'price': 9.99},
            {'name': 'Standard', 'price': 19.99},
            {'name': 'Premium', 'price': 29.99},
            {'name': 'Enterprise', 'price': 49.99}
        ]
        
        subscription_count = 0
        for user in users:
            if random.random() < 0.6:  # 60% of users have subscriptions
                plan = random.choice(subscription_plans)
                Subscription.objects.create(
                    user=user,
                    plan=plan['name'],
                    is_active=random.choice([True, True, False])  # 66% active
                )
                subscription_count += 1
        self.stdout.write(self.style.SUCCESS(f'✅ Created {subscription_count} subscriptions'))

        self.stdout.write(self.style.SUCCESS('📝 Creating generated content...'))
        # Create generated content with realistic types
        content_types = ['word', 'image']
        content_count = 0
        for user in users:
            for _ in range(random.randint(5, 20)):
                GeneratedContent.objects.create(
                    user=user,
                    content_type=random.choice(content_types),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                content_count += 1
        self.stdout.write(self.style.SUCCESS(f'✅ Created {content_count} pieces of generated content'))

        self.stdout.write(self.style.SUCCESS('📚 Creating blog posts...'))
        # Create blog posts with realistic categories and content
        categories = ['Technology', 'Business', 'Marketing', 'Development', 'AI', 'Cloud Computing', 'Cybersecurity']
        
        for i in range(20):
            author = random.choice(users)
            title = fake.catch_phrase()
            Blog.objects.create(
                title=title,
                slug=slugify(title),
                content='\n\n'.join(fake.paragraphs(nb=5)),
                excerpt=fake.paragraph(nb_sentences=1),
                author=author,
                category=random.choice(categories),
                tags=','.join(fake.words(nb=3)),
                is_published=True,
                views=random.randint(100, 10000),
                featured_image='blog/images/blog-01.png'
            )
            if (i + 1) % 5 == 0:
                self.stdout.write(self.style.SUCCESS(f'✅ Created {i + 1} blog posts'))

        self.stdout.write(self.style.SUCCESS('👥 Creating team members...'))
        # Create team members with realistic positions
        positions = [
            'Chief Executive Officer',
            'Chief Technology Officer',
            'Chief Operating Officer',
            'Senior Software Engineer',
            'Product Manager',
            'UX/UI Designer',
            'Marketing Director',
            'Sales Manager',
            'Data Scientist',
            'DevOps Engineer',
            'Customer Success Manager',
            'Business Analyst'
        ]
        
        # Create featured team members
        featured_members = [
            {'name': 'John Anderson', 'position': 'Chief Executive Officer'},
            {'name': 'Sarah Mitchell', 'position': 'Chief Technology Officer'},
            {'name': 'Michael Chen', 'position': 'Chief Operating Officer'}
        ]
        
        for i, member in enumerate(featured_members):
            TeamMember.objects.create(
                name=member['name'],
                position=member['position'],
                photo='team_photos/team-01.jpg',
                featured=True,
                order=i + 1
            )
        self.stdout.write(self.style.SUCCESS('✅ Created featured team members'))
        
        # Create non-featured team members
        for i in range(8):
            TeamMember.objects.create(
                name=fake.name(),
                position=random.choice(positions),
                photo='team_photos/team-01.jpg',
                featured=False,
                order=i + 4
            )
        self.stdout.write(self.style.SUCCESS('✅ Created non-featured team members'))

        self.stdout.write(self.style.SUCCESS('📝 Creating release notes...'))
        # Create release notes with realistic version numbers and features
        release_features = {
            'fixed': [
                'Fixed user authentication issues with OAuth providers',
                'Resolved data synchronization problems in real-time updates',
                'Fixed UI rendering bugs on mobile devices',
                'Fixed email notification delivery issues',
                'Resolved payment processing timeout errors',
                'Fixed dashboard chart loading problems',
                'Fixed user profile image upload issues',
                'Resolved search functionality performance issues'
            ],
            'updated': [
                'Updated payment processing system for better security',
                'Improved search functionality with advanced filters',
                'Enhanced user dashboard with new analytics',
                'Updated API endpoints for better performance',
                'Improved email templates and delivery system',
                'Enhanced mobile responsiveness across all pages',
                'Updated user onboarding flow for better UX',
                'Improved error handling and logging system'
            ],
            'improved': [
                'Improved application performance by 40%',
                'Enhanced security measures with 2FA support',
                'Optimized database queries for faster loading',
                'Improved AI model accuracy and response time',
                'Enhanced data backup and recovery system',
                'Improved user interface accessibility features',
                'Optimized image compression and loading',
                'Enhanced real-time collaboration features'
            ],
            'added': [
                'Added new reporting features with export options',
                'Implemented dark mode across the application',
                'Added multi-language support for 5 languages',
                'Added advanced analytics dashboard',
                'Implemented real-time chat support system',
                'Added automated backup and restore functionality',
                'Added user activity tracking and insights',
                'Implemented advanced search with AI suggestions'
            ]
        }
        
        for i in range(8):
            version = f"1.{i}.0"
            # Select random features for each release
            features = {}
            for feature_type in ['fixed', 'updated', 'improved', 'added']:
                features[feature_type] = random.sample(release_features[feature_type], random.randint(2, 4))
            
            ReleaseNote.objects.create(
                version=version,
                release_date=timezone.now() - timedelta(days=i*45),
                heading=f"Release {version} - {fake.catch_phrase()}",
                features=features
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Created release note for version {version}'))

        self.stdout.write(self.style.SUCCESS('❓ Creating FAQs...'))
        # Create FAQs with realistic categories and questions
        categories = ['General', 'Technical', 'Billing', 'Account', 'Security', 'Features', 'API', 'Integrations']
        faq_data = {
            'General': [
                'What is AIWave and how does it work?',
                'How do I get started with AIWave?',
                'What are the system requirements for AIWave?',
                'Is AIWave available on mobile devices?',
                'What languages does AIWave support?'
            ],
            'Technical': [
                'How do I integrate AIWave API into my application?',
                'What programming languages and frameworks are supported?',
                'How do I troubleshoot common integration issues?',
                'What are the API rate limits?',
                'How do I handle API authentication errors?'
            ],
            'Billing': [
                'What payment methods do you accept?',
                'How do I upgrade or downgrade my subscription plan?',
                'What is your refund and cancellation policy?',
                'Do you offer annual billing discounts?',
                'How do I view my billing history and invoices?'
            ],
            'Account': [
                'How do I reset my password if I forgot it?',
                'Can I change my email address associated with my account?',
                'How do I delete my account and all associated data?',
                'How do I enable two-factor authentication?',
                'Can I transfer my account to another user?'
            ],
            'Security': [
                'How secure is my data with AIWave?',
                'What security measures do you have in place?',
                'How do you handle data breaches and security incidents?',
                'Is my data encrypted in transit and at rest?',
                'Do you comply with GDPR and other privacy regulations?'
            ],
            'Features': [
                'What AI models and capabilities does AIWave support?',
                'Can I customize the AI responses and behavior?',
                'How do I export my data and conversations?',
                'What file formats are supported for uploads?',
                'Can I use AIWave offline or without internet?'
            ],
            'API': [
                'How do I get my API key and credentials?',
                'What are the different API endpoints available?',
                'How do I handle API response errors?',
                'Can I use webhooks for real-time notifications?',
                'What is the API documentation and examples?'
            ],
            'Integrations': [
                'Does AIWave integrate with popular platforms?',
                'How do I connect AIWave with my existing tools?',
                'Can I build custom integrations?',
                'What webhook events are available?',
                'How do I set up automated workflows?'
            ]
        }

        faq_answers = [
            "AIWave is a comprehensive AI-powered platform that helps businesses automate their workflows, generate content, and enhance productivity through advanced machine learning algorithms.",
            "Getting started is easy! Simply sign up for an account, choose your plan, and follow our step-by-step onboarding guide to set up your first AI workflow.",
            "AIWave works on any modern web browser and requires a stable internet connection. For mobile access, we recommend using our responsive web interface.",
            "Yes, AIWave is fully responsive and works seamlessly on mobile devices including smartphones and tablets.",
            "AIWave currently supports English, Spanish, French, German, and Chinese with more languages coming soon.",
            "Our API is RESTful and supports JSON responses. You can integrate it using any programming language that supports HTTP requests.",
            "We provide comprehensive documentation, code examples, and a developer community to help you troubleshoot any issues.",
            "Our standard rate limit is 1000 requests per hour per API key, with higher limits available for enterprise plans.",
            "We accept all major credit cards, PayPal, and bank transfers for enterprise customers.",
            "You can upgrade or downgrade your plan at any time from your account dashboard. Changes take effect immediately.",
            "We offer a 30-day money-back guarantee for all paid plans. You can cancel anytime from your account settings.",
            "Yes, we offer a 20% discount for annual billing compared to monthly plans.",
            "You can view your complete billing history and download invoices from your account dashboard.",
            "Use the 'Forgot Password' link on the login page to receive a password reset email with secure instructions.",
            "Yes, you can update your email address from your account settings. You'll need to verify the new email address.",
            "To delete your account, go to account settings and use the 'Delete Account' option. This action is irreversible.",
            "Two-factor authentication can be enabled in your security settings using authenticator apps or SMS.",
            "Your data is protected with enterprise-grade encryption and we never share it with third parties.",
            "We implement multiple layers of security including SSL encryption, regular security audits, and compliance with industry standards.",
            "In the unlikely event of a security incident, we have a comprehensive response plan and will notify affected users immediately.",
            "Yes, all data is encrypted using AES-256 encryption both in transit and at rest.",
            "We are fully compliant with GDPR, CCPA, and other relevant privacy regulations.",
            "AIWave supports multiple AI models including GPT-4, Claude, and our proprietary models for specialized tasks.",
            "Yes, you can customize AI responses through our advanced configuration options and training features.",
            "You can export your data in multiple formats including JSON, CSV, and PDF from your account dashboard.",
            "We support common file formats including PDF, DOCX, TXT, CSV, and various image formats.",
            "AIWave requires an internet connection for real-time AI processing, but you can work offline with cached data.",
            "API keys are available in your developer dashboard after account verification and plan activation.",
            "We provide comprehensive API documentation with examples in multiple programming languages.",
            "Our API returns detailed error codes and messages to help you identify and resolve issues quickly.",
            "Yes, webhooks are available for real-time notifications about important events and updates.",
            "Complete API documentation with examples is available in our developer portal.",
            "AIWave integrates with popular platforms including Slack, Microsoft Teams, Zapier, and many others.",
            "Our integration setup is straightforward with step-by-step guides for each supported platform.",
            "Yes, you can build custom integrations using our open API and webhook system.",
            "Available webhook events include user activity, content generation, and system updates.",
            "You can set up automated workflows using our visual workflow builder or API integrations."
        ]

        faq_count = 0
        for category in categories:
            for question in faq_data[category]:
                FAQ.objects.create(
                    category=category,
                    question=question,
                    answer=random.choice(faq_answers),
                    is_active=True
                )
                faq_count += 1
        self.stdout.write(self.style.SUCCESS(f'✅ Created {faq_count} FAQs'))

        self.stdout.write(self.style.SUCCESS('💬 Creating user queries...'))
        # Create user queries with realistic subjects and messages
        query_subjects = [
            'Account Access Issue - Cannot Login',
            'Billing Question - Unexpected Charges',
            'Feature Request - New Integration',
            'Technical Support - API Integration',
            'Partnership Inquiry - Business Development',
            'Bug Report - Dashboard Not Loading',
            'General Question - Pricing Plans',
            'Security Concern - Data Privacy',
            'Performance Issue - Slow Response Times',
            'Integration Problem - Webhook Not Working',
            'Subscription Management - Plan Change',
            'Data Export Request - GDPR Compliance',
            'API Documentation - Missing Examples',
            'Mobile App - Feature Request',
            'Customer Success - Onboarding Help'
        ]
        
        query_messages = [
            "I'm having trouble logging into my account. I've tried resetting my password but haven't received the email. Can you help me resolve this issue?",
            "I noticed some unexpected charges on my recent bill. I was only on the basic plan but was charged for premium features. Can you investigate this?",
            "I would love to see integration with our existing CRM system. This would greatly improve our workflow efficiency. Is this something you're planning to add?",
            "I'm trying to integrate your API into our application but encountering authentication errors. The documentation doesn't seem to cover this specific case.",
            "We're interested in exploring a partnership opportunity. Our company provides complementary services and we think there's great potential for collaboration.",
            "The dashboard is not loading properly on Chrome browser. I see a blank screen with just the header. This started happening after the recent update.",
            "I'm considering upgrading to a higher plan but would like to understand the differences between Standard and Premium plans in detail.",
            "I have concerns about data privacy and security. Can you provide more information about how my data is stored and protected?",
            "The application has been running very slowly for the past few days. Response times are taking 10-15 seconds when they used to be instant.",
            "Our webhook integration stopped working yesterday. We're not receiving any notifications. Can you check if there's an issue on your end?",
            "I need to change my subscription plan from monthly to annual billing. How do I do this and will I get the annual discount?",
            "I need to export all my data for GDPR compliance purposes. What format will this be in and how long does it take to process?",
            "The API documentation is missing examples for the new endpoints. Could you provide some code samples for Python and JavaScript?",
            "I use the mobile app daily and would love to see offline mode functionality. Is this something you're working on?",
            "We're new to the platform and would appreciate some guidance on best practices for setting up our workflows efficiently."
        ]
        
        for i in range(50):
            UserQueries.objects.create(
                name=fake.name(),
                email=fake.email(),
                subject=random.choice(query_subjects),
                phone=fake.phone_number(),
                message=random.choice(query_messages),
                is_read=random.choice([True, True, False])  # 66% read
            )
            if (i + 1) % 10 == 0:
                self.stdout.write(self.style.SUCCESS(f'✅ Created {i + 1} user queries'))

        self.stdout.write(self.style.SUCCESS('💭 Creating chat sessions and messages...'))
        # Create chat sessions and messages with realistic content
        session_count = 0
        message_count = 0
        for user in users:
            if random.random() < 0.7:  # 70% of users have chat sessions
                for _ in range(random.randint(1, 5)):
                    session = ChatSession.objects.create(
                        user=user,
                        bot_mode=random.choice(BOT_MODES),
                        title=fake.sentence()
                    )
                    session_count += 1
                    
                    # Create messages for each session
                    for _ in range(random.randint(3, 10)):
                        ChatMessage.objects.create(
                            session=session,
                            message=fake.paragraph(nb_sentences=1),
                            is_bot_response=random.choice([True, False]),
                            feedback_type=random.choice(['like', 'dislike', 'none'])
                        )
                        message_count += 1
        self.stdout.write(self.style.SUCCESS(f'✅ Created {session_count} chat sessions with {message_count} messages'))

        # Ensure superusers have profiles
        superuser_count = 0
        for superuser in User.objects.filter(is_superuser=True):
            UserProfile.objects.get_or_create(
                user=superuser,
                defaults={
                    'role': 'admin',
                    'is_active': True,
                    'department': 'Administration',
                    'designation': 'System Administrator'
                }
            )
            superuser_count += 1
        if superuser_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Ensured {superuser_count} superuser profiles exist'))

        self.stdout.write(self.style.SUCCESS('⚙️ Creating environment variables and settings...'))
        # Create environment variables
        env_vars = {
            'OPENAI_API_KEY': 'your-openai-key-here',
            'STRIPE_SECRET_KEY': 'sk_test_sample_key_for_testing',
            'AWS_ACCESS_KEY_ID': 'your-aws-access-key-id',
            'AWS_SECRET_ACCESS_KEY': 'your-aws-secret-access-key',
            'DATABASE_URL': 'postgresql://user:password@localhost:5432/aiwave_db',
            'REDIS_URL': 'redis://localhost:6379/0',
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'JWT_SECRET_KEY': 'your-super-secret-jwt-key-here',
            'ENCRYPTION_KEY': 'your-32-character-encryption-key'
        }
        
        for key, value in env_vars.items():
            EnvVar.objects.get_or_create(
                key=key,
                defaults={'value': value}
            )
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(env_vars)} environment variables'))
        
        # Create content settings
        content_settings = {
            'site_name': 'AIWave',
            'site_description': 'Advanced AI-powered platform for business automation',
            'contact_email': 'support@aiwave.com',
            'contact_phone': '+1 (555) 123-4567',
            'company_address': '123 AI Street, Tech City, TC 12345',
            'social_facebook': 'https://facebook.com/aiwave',
            'social_twitter': 'https://twitter.com/aiwave',
            'social_linkedin': 'https://linkedin.com/company/aiwave',
            'maintenance_mode': 'false',
            'registration_enabled': 'true',
            'default_language': 'en',
            'timezone': 'UTC',
            'max_file_size': '10485760',  # 10MB
            'allowed_file_types': 'jpg,jpeg,png,pdf,doc,docx,txt'
        }
        
        for key, value in content_settings.items():
            ContentSetting.objects.get_or_create(
                key=key,
                defaults={'value': value}
            )
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(content_settings)} content settings'))

        self.stdout.write(self.style.SUCCESS('🎉 Successfully populated all dummy data!')) 