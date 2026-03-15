from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from service.models import BikeService
from django.db.models import Sum

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect("home")
        
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

def logout_view(request):
    auth_logout(request)
    return redirect("login")

def start_page(request):
    return render(request, "start.html")

@login_required(login_url='login')
def home_page(request):
    return render(request, "home.html", {'user': request.user})

def about_page(request):
    return render(request, "about.html")

def contact_page(request):
    return render(request, "contact.html")

def register_page(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("cpassword", "").strip()

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "register.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = fullname
        user.save()

        auth_login(request, user)
        return redirect("home")

    return render(request, "register.html")

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

# -----------------------------------------------------------------
# Service Centre details — update these to match your actual centre
# -----------------------------------------------------------------
SERVICE_CENTRE_NAME    = "ABC Bike Service Centre"
SERVICE_CENTRE_ADDRESS = "123 Service Road, Trichy, Tamil Nadu, India"
SERVICE_CENTRE_MAPS    = "https://maps.google.com/?q=Trichy+Bike+Service+Centre"
SERVICE_CENTRE_PHONE   = "+91 98765 43210"
# The in-app contact page (relative — we build the full URL in the view)
SERVICE_CENTRE_PAGE    = "/contact/"

@login_required(login_url='login')
def service_page(request):
    if request.method == "POST":
        model = request.POST.get("model", "")
        km    = request.POST.get("km") or 0
        last  = request.POST.get("lastService") or 0
        phone = request.POST.get("phone", "")
        email = request.POST.get("email", "")

        try:
            # ── 1. Save Record ──────────────────────────────────────────
            BikeService.objects.create(
                user=request.user,
                model=model,
                total_km=int(km),
                last_service_km=int(last),
                phone=phone,
                email=email
            )

            # ── 2. Service-due alert logic (2 500 KM threshold) ─────────
            km_diff   = int(km) - int(last)
            alert_msg = (
                f"⚠ URGENT: Your {model} is due for service! "
                f"(Running {km_diff} KM since last service)"
                if km_diff >= 2500 else
                f"✔ Your {model} is in good condition. "
                f"Next service in {2500 - km_diff} KM."
            )

            # ── 3. Build the full site base URL for links in email ──────
            scheme       = "https" if request.is_secure() else "http"
            base_url     = f"{scheme}://{request.get_host()}"
            contact_link = f"{base_url}{SERVICE_CENTRE_PAGE}"

            # ── 4. Send HTML Email with service centre link ─────────────
            if email:
                subject      = f"Bike Service Update – {model}"
                status_class = "urgent" if km_diff >= 2500 else "ok"

                # Plain-text fallback
                text_body = f"""Hello {request.user.username},

Your service record has been updated.

Details:
  Model         : {model}
  Current KM    : {km} KM
  Last Service  : {last} KM

Status: {alert_msg}

================================
Visit Our Service Centre
================================
{SERVICE_CENTRE_NAME}
Address : {SERVICE_CENTRE_ADDRESS}
Phone   : {SERVICE_CENTRE_PHONE}

Get Directions : {SERVICE_CENTRE_MAPS}
Contact Page   : {contact_link}

Regards,
Bike Service Team
"""

                # HTML email
                html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body  {{ font-family: Arial, sans-serif; background:#f4f4f4; margin:0; padding:0; }}
    .wrap {{ max-width:600px; margin:30px auto; background:#fff;
             border-radius:10px; overflow:hidden;
             box-shadow:0 4px 15px rgba(0,0,0,.1); }}
    .hdr  {{ background:linear-gradient(135deg,#1a1a2e,#16213e);
             color:#fff; padding:30px 40px; text-align:center; }}
    .hdr h1 {{ margin:0; font-size:22px; }}
    .hdr p  {{ margin:6px 0 0; font-size:13px; opacity:.75; }}
    .body {{ padding:30px 40px; color:#333; }}
    .body h2 {{ color:#1a1a2e; margin-top:0; }}
    .info-box {{ background:#f8f9ff; border-left:4px solid #4f8ef7;
                 border-radius:6px; padding:16px 20px; margin:20px 0; }}
    .info-box p {{ margin:6px 0; font-size:14px; }}
    .status {{ border-radius:8px; padding:14px 18px; margin:20px 0;
               font-weight:bold; font-size:15px; }}
    .urgent {{ background:#fff0f0; color:#c0392b; border:1px solid #f5c6cb; }}
    .ok     {{ background:#f0fff4; color:#2d6a4f; border:1px solid #c3e6cb; }}
    .cta    {{ background:#f8f9ff; border-radius:10px; padding:24px;
               margin:24px 0; text-align:center; }}
    .cta h3 {{ color:#1a1a2e; margin-top:0; }}
    .cta p  {{ font-size:13px; color:#555; margin:4px 0; }}
    .btn    {{ display:inline-block; margin:8px 6px 0; padding:12px 22px;
               border-radius:6px; font-size:14px; font-weight:bold;
               text-decoration:none; color:#fff; }}
    .btn-maps    {{ background:#4f8ef7; }}
    .btn-contact {{ background:#1a1a2e; }}
    .footer {{ text-align:center; padding:20px; font-size:12px; color:#aaa; }}
  </style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <h1>&#x1F3CD;&#xFE0F; Bike Service Update</h1>
    <p>Service record for <strong>{model}</strong></p>
  </div>
  <div class="body">
    <h2>Hello, {request.user.username}!</h2>
    <p>Your service check has been completed. Here are your details:</p>
    <div class="info-box">
      <p><strong>Model:</strong> {model}</p>
      <p><strong>Current KM:</strong> {km} KM</p>
      <p><strong>Last Service:</strong> {last} KM</p>
      <p><strong>Phone:</strong> {phone}</p>
    </div>
    <div class="status {status_class}">{alert_msg}</div>
    <div class="cta">
      <h3>&#x1F527; {SERVICE_CENTRE_NAME}</h3>
      <p>&#x1F4CD; {SERVICE_CENTRE_ADDRESS}</p>
      <p>&#x1F4DE; {SERVICE_CENTRE_PHONE}</p>
      <a href="{SERVICE_CENTRE_MAPS}" class="btn btn-maps" target="_blank">
        &#x1F4CC; Get Directions
      </a>
      <a href="{contact_link}" class="btn btn-contact" target="_blank">
        &#x1F310; Contact Us
      </a>
    </div>
    <p style="font-size:13px;color:#777;">
      We have also sent an SMS notification to <strong>{phone}</strong>.
    </p>
  </div>
  <div class="footer">
    &copy; 2025 Bike Service Team &nbsp;|&nbsp; Automated notification.
  </div>
</div>
</body>
</html>"""
                try:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_body,
                        from_email=settings.EMAIL_HOST_USER,
                        to=[email],
                    )
                    msg.attach_alternative(html_body, "text/html")
                    msg.send()
                    print(f"📧 HTML Email sent to {email}")
                except Exception as e:
                    print(f"❌ Email failed: {e}")

            # ── 5. SMS via Twilio ────────────────────────────────────────
            if phone:
                try:
                    from twilio.rest import Client
                    account_sid   = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
                    auth_token    = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
                    twilio_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

                    if account_sid and auth_token and twilio_number:
                        client = Client(account_sid, auth_token)
                        formatted_phone = phone
                        if len(phone) == 10 and phone.isdigit():
                            formatted_phone = "+91" + phone
                        elif not phone.startswith('+'):
                            formatted_phone = "+" + phone

                        sms_body = (
                            f"Hello {request.user.username}, "
                            f"Service checked for {model}. {alert_msg} "
                            f"Visit us: {SERVICE_CENTRE_MAPS}"
                        )
                        sms = client.messages.create(
                            body=sms_body,
                            from_=twilio_number,
                            to=formatted_phone
                        )
                        print(f"📱 [TWILIO SMS] Sent ID: {sms.sid} to {formatted_phone}")
                    else:
                        print(f"📱 [MOCK SMS] Twilio not configured. Would send to {phone}: {alert_msg}")
                except ImportError:
                    print(f"📱 [MOCK SMS] Install twilio (pip install twilio) for real SMS.")
                except Exception as e:
                    print(f"📱 [SMS ERROR] {e}")

            return render(request, "service.html", {
                "success": True,
                "alert_msg": alert_msg,
                "service_centre_name":    SERVICE_CENTRE_NAME,
                "service_centre_address": SERVICE_CENTRE_ADDRESS,
                "service_centre_phone":   SERVICE_CENTRE_PHONE,
                "service_centre_maps":    SERVICE_CENTRE_MAPS,
                "contact_link":           contact_link,
            })

        except Exception as e:
            print(e)
            return render(request, "service.html", {"success": False})

    return render(request, "service.html")

@login_required(login_url='login')
def message_page(request):
    return render(request, "message.html")

from django.db.models import Sum, Count

@login_required(login_url='login')
def analysis_page(request):
    qs = BikeService.objects.filter(user=request.user)
    
    total_services = qs.count()
    full_km = qs.aggregate(Sum('total_km'))['total_km__sum'] or 0
    
    # Chart Data
    model_stats = qs.values('model').annotate(count=Count('id'))
    
    labels = [item['model'] for item in model_stats]
    data = [item['count'] for item in model_stats]
    
    context = {
        'total_services': total_services,
        'total_km': full_km,
        'chart_labels': labels,
        'chart_data': data
    }
    return render(request, "analysis.html", context)

@login_required(login_url='login')
def history_page(request):
    services = BikeService.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "history.html", {'services': services})

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_page(request):
    services = BikeService.objects.all().order_by('-created_at')
    return render(request, "admin.html", {'services': services})
