import json
from app import create_app, db
from app.models import MicroLesson, Category

# High-quality micro-lesson content
lessons_data = {
    "Phishing": {
        "title": "Mastering Phishing Detection",
        "content_text": """Phishing remains the most common entry point for cyberattacks. It involves fraudulent communications that appear to come from a trustworthy source.

**Key Indicators of Phishing:**
1. **Urgency & Threats:** Emails claiming immediate action often bypass critical thinking (e.g., 'Account suspended', 'Urgent Payment').
2. **Generic Greetings:** 'Dear Customer' instead of your name often indicates a mass campaign.
3. **Mismatched Domains:** Check the sender address carefully. 'support@paypal-secure-update.com' is NOT paypal.com.
4. **Suspicious Links:** Hover over links (without clicking) to see the actual destination URL.
5. **Unexpected Attachments:** Never open invoices, receipts, or shipping documents you weren't expecting.

**Defense Strategy:**
- Verify out-of-band: If an email claims to be from your CEO asking for a wire transfer, call them or walk to their desk.
- Report suspicious emails using the 'Report Phishing' button.
- Do not trust display names; look at the actual email address.""",
        "quiz": [
            {"question": "What is the most common emotional trigger used in phishing?", "options": ["Curiosity", "Urgency/Fear", "Happiness", "Boredom"], "correct_answer": "Urgency/Fear"},
            {"question": "You receive an email from 'IT-Support' asking for your password validation. What do you do?", "options": ["Reply with password", "Click the link provided", "Report as Phishing", "Ignore it"], "correct_answer": "Report as Phishing"},
            {"question": "When hovering over a link, the URL looks different from the text. This is a sign of:", "options": ["URL Masking/Spoofing", "Secure Redirection", "Load Balancing", "Email Encryption"], "correct_answer": "URL Masking/Spoofing"}
        ]
    },
    "Pretexting": {
        "title": "Defending Against Pretexting",
        "content_text": """Pretexting is a social engineering technique where attackers create a fabricated scenario (the pretext) to steal information.

**Common Pretexts:**
1. **The 'Help Desk' Scam:** Calling claiming to be IT support needing your password to 'fix a virus'.
2. **The 'Executive' Impersonation:** Pretending to be a VP or CEO in a rush, needing immediate assistance.
3. **The 'Vendor' Check:** Claiming to be a supplier updating records to get invoice details.

**Defense Strategy:**
- **Challenge Protocol:** Always verify the identity of the requester. 'Can I call you back on your official extension?'
- **Zero Trust for Credentials:** Legitimate support staff will NEVER ask for your password.
- **Guard Personal Info:** Don't reveal internal terminology or organizational structure to unknowns.""",
        "quiz": [
            {"question": "What distinguishes pretexting from simple phishing?", "options": ["It uses email only", "It involves a fabricated scenario/character", "It is always automated", "It targets only home users"], "correct_answer": "It involves a fabricated scenario/character"},
            {"question": "A caller claims to be the CEO requiring immediate data. What is the best response?", "options": ["Send data immediately", "Verify via official callback", "Ask them to email personal account", "Refuse RUDELY"], "correct_answer": "Verify via official callback"},
            {"question": "Legitimate IT support will never ask for:", "options": ["Your IP address", "Error messages", "Your Password", "Screenshot of the issue"], "correct_answer": "Your Password"}
        ]
    },
    "Baiting": {
        "title": "The Danger of Physical Baiting",
        "content_text": """Baiting uses physical media (USB drives, CD-ROMs) or enticing downloads to trick victims.

**The Attack Vector:**
Attackers leave infected USB drives in parking lots, lobbies, or even mail them to employees. The labels are tempting: 'Q4 Salaries', 'Layoff Plan', or 'Employee Photos'.

**Why it works:**
Curiosity is powerful. When plugged in, 'Human Interface Device' (HID) attacks can execute scripts immediately, installing malware or establishing remote access.

**Defense Strategy:**
- **Never plug found media:** Treat any unknown USB drive as infected.
- **Hand it to Security:** If you find a device, do not plug it in. Give it to the security team.
- **Disable Auto-Run:** Ensure your operating system does not automatically run programs from external drives.""",
        "quiz": [
            {"question": "You find a USB drive labeled 'Executive Salaries' in the lobby. What do you do?", "options": ["Plug it in to check owner", "Take it home", "Hand to Security Team", "Leave it there"], "correct_answer": "Hand to Security Team"},
            {"question": "What type of attack executes immediately upon plugging in a USB?", "options": ["HID / Auto-Run Attack", "Phishing", "Vishing", "DDoS"], "correct_answer": "HID / Auto-Run Attack"},
            {"question": "Baiting relies primarily on which human trait?", "options": ["Fear", "Curiosity", "Greed", "Laziness"], "correct_answer": "Curiosity"}
        ]
    },
    "Quid Pro Quo": {
        "title": "Something for Something: Quid Pro Quo",
        "content_text": """Quid Pro Quo attacks offer a benefit in exchange for information. Unlike baiting, it's often a service rather than a good.

**Examples:**
- **'Free WiFi' Surveys:** 'Give us your password to access faster internet.'
- **The 'Support' Call:** Calling random numbers claiming to be 'Tech Support' offering to fix a slow computer if the user grants remote access.
- **Gifts for Surveys:** Offering gift cards in exchange for detailed internal network information.

**Defense Strategy:**
- **No Free Lunch:** Be skeptical of unsolicited offers of help or upgrades.
- **Verify Sources:** Only accept support from known, verified vendors or internal teams.
- **Protect Credentials:** Never trade passwords for services or gifts.""",
        "quiz": [
            {"question": "Quid Pro Quo translates to:", "options": ["Seize the day", "Something for Something", "Buyer Beware", "Trust No One"], "correct_answer": "Something for Something"},
            {"question": "An external caller offers to 'speed up your PC' if you give remote access. This is:", "options": ["Good customer service", "Quid Pro Quo / Tech Support Scam", "Whaling", "Dumpster Diving"], "correct_answer": "Quid Pro Quo / Tech Support Scam"},
            {"question": "What is the primary difference between Baiting and Quid Pro Quo?", "options": ["Baiting uses goods; Quid Pro Quo uses services", "Baiting is online only", "Quid Pro Quo is legal", "No difference"], "correct_answer": "Baiting uses goods; Quid Pro Quo uses services"}
        ]
    },
    "Tailgating": {
        "title": "Physical Security: Preventing Tailgating",
        "content_text": """Tailgating (or Piggybacking) is when an unauthorized person follows an authorized person into a secure area.

**How it happens:**
- **The 'Polite' Hold:** An attacker walks up behind you with hands full of boxes/coffee, expecting you to hold the door.
- **The Smoker's Dock:** Joining employees re-entering from a smoke break.
- **The Forgotten Badge:** Claiming they forgot their ID inside.

**Defense Strategy:**
- **One Badge, One Entry:** Every person must scan their own badge.
- **Challenge Strangers:** 'I don't recognize you, please check in at the front desk.'
- **Don't hold the door:** It feels rude, but it's secure. Direct them to the reception.""",
        "quiz": [
            {"question": "What is the 'One Badge, One Entry' rule?", "options": ["Everyone wears one badge", "Only one person per day", "Every individual must scan to enter", "Badges are for single use"], "correct_answer": "Every individual must scan to enter"},
            {"question": "A person with heavy boxes asks you to hold the secure door. You should:", "options": ["Hold it open", "Ask them to badge in first", "Help them carry boxes", "Ignore them completely"], "correct_answer": "Ask them to badge in first"},
            {"question": "Tailgating exploits which social norm?", "options": ["Greed", "Politeness/Courtesy", "Fear", "Competition"], "correct_answer": "Politeness/Courtesy"}
        ]
    },
    "Vishing": {
        "title": "Voice Phishing (Vishing) Defense",
        "content_text": """Vishing moves the attack to the phone. The human voice can be very persuasive and harder to fact-check in real-time.

**Tactics:**
- **Spoofing Caller ID:** Making the call look like it comes from 'HQ' or 'The Bank'.
- **The 'IRS/Tax' Scam:** Threatening arrest if payment isn't made immediately.
- **Technical Support Scams:** Claiming your computer is sending error messages.

**Defense Strategy:**
- **Don't trust Caller ID:** It is easily faked.
- **Hang up and Call Back:** If they claim to be your bank, hang up and dial the number on the back of your card.
- **Verify Identity:** Ask for a ticket number or extension and verify it in the corporate directory.""",
        "quiz": [
            {"question": "Vishing stands for:", "options": ["Virtual Phishing", "Voice Phishing", "Visual Phishing", "Video Phishing"], "correct_answer": "Voice Phishing"},
            {"question": "If a caller claims to be your bank detecting fraud, the safest action is:", "options": ["Give card details", "Confirm your DOB", "Hang up and call the number on your card", "Ask for their manager"], "correct_answer": "Hang up and call the number on your card"},
            {"question": "Can Caller ID signal be spoofed/faked?", "options": ["No, it's regulated", "Yes, easily", "Only by government", "Only on landlines"], "correct_answer": "Yes, easily"}
        ]
    },
    "Smishing": {
        "title": "SMS Phishing (Smishing) Awareness",
        "content_text": """Smishing targets users via text messages. We are often less guarded with texts than emails.

**Common Scams:**
- **Delivery Alerts:** 'Your package delivery failed. Click here to reschedule.'
- **Bank Alerts:** 'Suspicious activity detected. Log in to verify.'
- **MFA Bypass:** 'Here is your code. Please read it to me.'

**Defense Strategy:**
- **Context Awareness:** Did you order a package? If not, ignore the 'delivery failed' text.
- **Avoid clicking links:** Navigate to the service (FedEx, Bank, Amazon) via your browser app, not the SMS link.
- **Never share OTPs:** OTPs are for YOU. No legitimate agent will ever ask you to read a code to them.""",
        "quiz": [
            {"question": "A text says 'Your Netflix payment failed, click to update'. You should:", "options": ["Click link immediately", "Reply 'STOP'", "Log in via the official Netflix app/site to check", "Forward to friends"], "correct_answer": "Log in via the official Netflix app/site to check"},
            {"question": "Smishing refers to phishing via:", "options": ["Social Media", "SMS / Text Message", "Small Emails", "Smartphones only"], "correct_answer": "SMS / Text Message"},
            {"question": "Why are OTP (One Time Password) requests via SMS dangerous?", "options": ["They cost money", "Attackers try to trick you into sharing them to bypass 2FA", "They are always fake", "They drain battery"], "correct_answer": "Attackers try to trick you into sharing them to bypass 2FA"}
        ]
    },
    "WiFi_Evil_Twin": {
        "title": "Public Wi-Fi Risks: The Evil Twin",
        "content_text": """An 'Evil Twin' is a rogue Wi-Fi access point set up by an attacker to look like a legitimate network.

**Scenario:**
You are at 'Starbucks'. You see two networks: 'Google Starbucks' and 'Starbucks_Free_WiFi'. One might be an attacker's laptop broadcasting a fake signal. If you connect, all your traffic goes through them.

**Defense Strategy:**
- **Verify Network Name:** Ask staff for the exact name.
- **Use VPN:** Always use a VPN on public Wi-Fi. It creates an encrypted tunnel, protecting your data even if the network is malicious.
- **Avoid Sensitive Transactions:** Don't do banking or corporate login on untrusted public Wi-Fi without a VPN.""",
        "quiz": [
            {"question": "What is an 'Evil Twin' in cybersecurity?", "options": ["A duplicate file", "A malicious Wi-Fi access point mimicking a real one", "A cloned credit card", "A phishing email"], "correct_answer": "A malicious Wi-Fi access point mimicking a real one"},
            {"question": "What is the best protection when using public Wi-Fi?", "options": ["Incognito Mode", "Antivirus", "VPN (Virtual Private Network)", "Strong Password"], "correct_answer": "VPN (Virtual Private Network)"},
            {"question": "If you see two networks with similar names at a cafe, you should:", "options": ["Pick the strongest signal", "Connect to both", "Ask staff for the official name", "Pick the one without a password"], "correct_answer": "Ask staff for the official name"}
        ]
    },
    "Honeytraps": {
        "title": "Social Engineering: Honeytraps",
        "content_text": """Honeytraps involve an attacker establishing a fake romantic or friendly relationship to extract information or manipulate the victim.

**The Process:**
1. **Selection:** Identifying targets with access to sensitive info.
2. **Contact:** Meeting via dating apps, LinkedIn, or social media.
3. **Grooming:** Building trust over weeks or months.
4. **Extraction:** Casually asking for work secrets, or sending a 'photo' that is actually malware.

**Defense Strategy:**
- **Separate Work/Life:** Be cautious discussing specific work projects with new online acquaintances.
- **Reverse Image Search:** Check if their profile photo is a stock image or stolen.
- **Policy Compliance:** Never share internal documents, no matter how much you trust the person.""",
        "quiz": [
            {"question": "Honeytraps primarily exploit:", "options": ["Technical vulnerabilities", "Emotional/Social connections", "Physical locks", "Financial greed"], "correct_answer": "Emotional/Social connections"},
            {"question": "A new online friend asks for a screenshot of your internal work dashboard 'just to see what it looks like'. You should:", "options": ["Send it", "Blur the text and send", "Refuse and suspect a trap", "Send a fake one"], "correct_answer": "Refuse and suspect a trap"},
            {"question": "What is 'Grooming' in this context?", "options": ["Cleaning up data", "Building trust over time to lower defenses", "Installing malware", "Password cracking"], "correct_answer": "Building trust over time to lower defenses"}
        ]
    },
    "Insider_Threats": {
        "title": "Understanding Insider Threats",
        "content_text": """An insider threat comes from within the organization—employees, contractors, or partners who have authorized access but misuse it.

**Types:**
1. **Malicious Insider:** Intentionally steals data for profit or revenge.
2. **Negligent Insider:** The most common type. An employee trying to be helpful or cutting corners (e.g., holding the door, sharing passwords, losing a laptop).
3. **Compromised Insider:** An employee whose account has been hijacked by an attacker.

**Defense Strategy:**
- **Least Privilege:** Users should only have access to what they need.
- **See Something, Say Something:** Report unusual behavior (e.g., accessing data at odd hours, mass downloading).
- **Lock Your Screen:** Always lock your computer when walking away.""",
        "quiz": [
            {"question": "Which type of insider threat is the most common?", "options": ["Malicious Insider (Spy)", "Negligent Insider (Careless)", "Compromised Insider", "Inactive Insider"], "correct_answer": "Negligent Insider (Careless)"},
            {"question": "What does 'Least Privilege' mean?", "options": ["Users have no rights", "Users act like guests", "Users have only the access necessary for their job", "Admins have all power"], "correct_answer": "Users have only the access necessary for their job"},
            {"question": "You see a colleague downloading the entire customer database to a personal USB. What should you do?", "options": ["Help them", "Ask for a copy", "Report to Security/Management", "Ignore it"], "correct_answer": "Report to Security/Management"}
        ]
    }
}

def seed_micro_lessons():
    app = create_app()
    with app.app_context():
        print("Starting Micro-Lesson Seeding...")
        
        for cat_name, data in lessons_data.items():
            category = Category.query.filter_by(category_name=cat_name).first()
            if not category:
                # Create category if missing (fallback)
                print(f"Warning: Category {cat_name} not found, creating placeholder.")
                category = Category(category_name=cat_name, description=f"Lessons about {cat_name}")
                db.session.add(category)
                db.session.commit()
            
            # Check if lesson exists
            lesson = MicroLesson.query.filter_by(category_id=category.category_id, title=data['title']).first()
            
            if lesson:
                print(f"Updating {cat_name} lesson...")
                lesson.content_text = data['content_text']
                lesson.quiz_json = {"questions": data['quiz']}
            else:
                print(f"Creating {cat_name} lesson...")
                lesson = MicroLesson(
                    category_id=category.category_id,
                    title=data['title'],
                    content_text=data['content_text'],
                    est_time_minutes=5,
                    quiz_json={"questions": data['quiz']}
                )
                db.session.add(lesson)
        
        db.session.commit()
        print("Micro-Lessons seeded successfully!")

if __name__ == "__main__":
    seed_micro_lessons()
