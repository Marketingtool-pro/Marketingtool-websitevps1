from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings
from wowdash_app.env_cache import get
import smtplib
import ssl


class Command(BaseCommand):
    help = 'Test email functionality and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to',
        )
        parser.add_argument(
            '--check-config',
            action='store_true',
            help='Check email configuration without sending',
        )

    def handle(self, *args, **options):
        if options['check_config']:
            self.check_email_config()
        else:
            test_email = options['email'] or 'test@example.com'
            self.test_email_sending(test_email)

    def check_email_config(self):
        """Check email configuration settings"""
        self.stdout.write(self.style.SUCCESS('=== Email Configuration Check ==='))
        
        # Get email settings from env cache
        email_host = get('EMAIL_HOST')
        email_port = get('EMAIL_PORT')
        email_host_user = get('EMAIL_HOST_USER')
        email_host_password = get('EMAIL_HOST_PASSWORD')
        email_use_tls = get('EMAIL_USE_TLS')
        default_from_email = get('DEFAULT_FROM_EMAIL')
        email_backend = get('EMAIL_BACKEND')
        
        self.stdout.write(f'EMAIL_HOST: {email_host}')
        self.stdout.write(f'EMAIL_PORT: {email_port}')
        self.stdout.write(f'EMAIL_HOST_USER: {email_host_user}')
        self.stdout.write(f'EMAIL_HOST_PASSWORD: {"*" * len(email_host_password) if email_host_password else "Not set"}')
        self.stdout.write(f'EMAIL_USE_TLS: {email_use_tls}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {default_from_email}')
        self.stdout.write(f'EMAIL_BACKEND: {email_backend}')
        
        # Check if all required settings are present
        missing_settings = []
        if not email_host:
            missing_settings.append('EMAIL_HOST')
        if not email_port:
            missing_settings.append('EMAIL_PORT')
        if not email_host_user:
            missing_settings.append('EMAIL_HOST_USER')
        if not email_host_password:
            missing_settings.append('EMAIL_HOST_PASSWORD')
        if not default_from_email:
            missing_settings.append('DEFAULT_FROM_EMAIL')
        if not email_backend:
            missing_settings.append('EMAIL_BACKEND')
        
        if missing_settings:
            self.stdout.write(self.style.ERROR(f'Missing email settings: {", ".join(missing_settings)}'))
        else:
            self.stdout.write(self.style.SUCCESS('All email settings are configured'))
        
        # Test SMTP connection
        self.test_smtp_connection(email_host, email_port, email_host_user, email_host_password, email_use_tls)

    def test_smtp_connection(self, host, port, username, password, use_tls):
        """Test SMTP connection"""
        self.stdout.write('\n=== SMTP Connection Test ===')
        
        if not all([host, port, username, password]):
            self.stdout.write(self.style.ERROR('Cannot test SMTP connection - missing credentials'))
            return
        
        try:
            # Create SMTP connection
            if use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(host, port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP(host, port)
            
            # Login
            server.login(username, password)
            self.stdout.write(self.style.SUCCESS('SMTP connection successful'))
            
            # Close connection
            server.quit()
            
        except smtplib.SMTPAuthenticationError:
            self.stdout.write(self.style.ERROR('SMTP Authentication failed - check username and password'))
        except smtplib.SMTPConnectError:
            self.stdout.write(self.style.ERROR('SMTP Connection failed - check host and port'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'SMTP connection error: {str(e)}'))

    def test_email_sending(self, test_email):
        """Test sending an email"""
        self.stdout.write(self.style.SUCCESS('=== Email Sending Test ==='))
        
        # Get email settings
        email_host = get('EMAIL_HOST')
        email_port = get('EMAIL_PORT')
        email_host_user = get('EMAIL_HOST_USER')
        email_host_password = get('EMAIL_HOST_PASSWORD')
        email_use_tls = get('EMAIL_USE_TLS')
        default_from_email = get('DEFAULT_FROM_EMAIL')
        
        if not all([email_host, email_port, email_host_user, email_host_password, default_from_email]):
            self.stdout.write(self.style.ERROR('Email settings not properly configured'))
            return
        
        try:
            # Send test email
            subject = 'Test Email from Wowdash'
            message = f"""
            This is a test email from your Wowdash application.
            
            Email Configuration:
            - Host: {email_host}
            - Port: {email_port}
            - From: {default_from_email}
            - To: {test_email}
            
            If you receive this email, your email configuration is working correctly!
            """
            
            # Send the email
            result = send_mail(
                subject=subject,
                message=message,
                from_email=default_from_email,
                recipient_list=[test_email],
                fail_silently=False,
            )
            
            if result == 1:
                self.stdout.write(self.style.SUCCESS(f'Test email sent successfully to {test_email}'))
                self.stdout.write('Please check your email inbox (and spam folder) to confirm receipt.')
            else:
                self.stdout.write(self.style.ERROR('Failed to send test email'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending test email: {str(e)}'))
            self.stdout.write('This could be due to:')
            self.stdout.write('- Incorrect email credentials')
            self.stdout.write('- Network connectivity issues')
            self.stdout.write('- SMTP server restrictions')
            self.stdout.write('- Gmail app password not configured properly') 