import json
from app import create_app, db
from app.models import MicroLesson, Category

# Raw content provided by user
raw_content = {
    "Phishing": [
        {
            "question_text": "You receive an email from \"IT Support\" saying your password will expire today and you must click a link to keep your account active. The sender address is it-support@security-it-updates.com and the link points to http://login.company-secure-check.com. What is the safest action?",
            "question_type": "scenario_mcq",
            "options": [
                "Click the link and change your password immediately",
                "Forward the email to a colleague and ask if they got it too",
                "Open your browser and go directly to the official company portal URL you already know, then check for any alerts",
                "Reply to the email and ask them to confirm it is legitimate"
            ],
            "correct_option_index": 2
        },
        {
            "question_text": "Fill in the blank: The DNS record that specifies which mail servers are allowed to send email for a domain is called ______.",
            "question_type": "fill_blank",
            "correct_answer": "SPF"
        },
        {
            "question_text": "Which of the following is the BEST indication that an email might be a phishing attempt?",
            "question_type": "mcq",
            "options": [
                "The message uses your first name",
                "The email contains a company logo and footer",
                "The sender asks you to enter your credentials on a page reached through a shortened or unfamiliar URL",
                "The email arrives during normal business hours"
            ],
            "correct_option_index": 2
        },
        {
            "question_text": "Match each phishing term with its description",
            "question_type": "matching",
            "pairs": {
                "Spear phishing": "Highly targeted email aimed at a specific person or small group, often using personal details",
                "Business Email Compromise (BEC)": "Attacker compromises or spoofs an executive's mailbox to request transfers or sensitive data",
                "Clone phishing": "Attacker re-sends a legitimate email with a malicious attachment or link swapped in"
            }
        },
        {
            "question_text": "You inspect an email header and see that SPF and DKIM both fail for the sending domain. What is the most appropriate action?",
            "question_type": "scenario_mcq",
            "options": [
                "Ignore the failures because the email looks visually correct",
                "Treat the message as suspicious and follow the company's reporting procedure",
                "Forward the message to all colleagues to warn them",
                "Click the link but avoid entering your credentials"
            ],
            "correct_option_index": 1
        }
    ],
    "Pretexting": [
        {
            "question_text": "A caller claims to be from the IT helpdesk and says, \"We detected malware on your device. To fix this quickly, I need your username and password.\" The caller sounds confident and uses internal terminology. What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Provide the credentials so they can remove the malware quickly",
                "Ask them to send a follow-up email and reply with your credentials there",
                "Refuse to share your password, end the call, and contact IT through an official channel you already know",
                "Ask them a few technical questions and if the answers sound correct, share your password"
            ],
            "correct_option_index": 2
        },
        {
            "question_text": "Fill in the blank: Pretexting attacks often rely on creating a convincing ______, such as posing as HR, a manager, or a trusted vendor.",
            "question_type": "fill_blank",
            "correct_answer": "story"
        },
        {
            "question_text": "Which psychological principle is MOST often abused in pretexting attacks?",
            "question_type": "mcq",
            "options": [
                "Curiosity about new technology",
                "Respect for authority and desire to be helpful",
                "Love of discounts and free items",
                "Fear of public speaking"
            ],
            "correct_option_index": 1
        },
        {
            "question_text": "Match the impersonation role to the likely information they will try to obtain",
            "question_type": "matching",
            "pairs": {
                "Fake HR representative": "Employee personal data such as address, ID numbers, and bank details",
                "Fake vendor account manager": "Billing details, purchase orders, and payment account changes",
                "Fake internal auditor": "Access logs, financial records, and privileged system access justification"
            }
        },
        {
            "question_text": "In a chat message, someone claiming to be your manager says, \"I’m in a meeting and locked out of my account. Send me the client contract and internal pricing immediately via your personal email.\" What is the best response?",
            "question_type": "scenario_mcq",
            "options": [
                "Send the information to be helpful; it sounds urgent",
                "Ask for the client name and send the data without further checks",
                "Politely refuse and verify the request by calling your manager using an official number or messaging channel",
                "Send only part of the information so the risk is lower"
            ],
            "correct_option_index": 2
        }
    ],
    "Baiting": [
        {
            "question_text": "You find a USB drive in the office parking lot labeled \"Employee Salaries Q4\". What is the safest course of action?",
            "question_type": "scenario_mcq",
            "options": [
                "Plug it into your work laptop to see who it belongs to",
                "Plug it into your personal device at home instead of work",
                "Give it to IT or security according to company policy without connecting it to any device",
                "Leave it on your colleague's desk so they can decide"
            ],
            "correct_option_index": 2
        },
        {
            "question_text": "Fill in the blank: Baiting attacks exploit a target's ______, often by offering something tempting like \"confidential\" files or free media.",
            "question_type": "fill_blank",
            "correct_answer": "curiosity"
        },
        {
            "question_text": "Which of the following is the BEST example of a digital baiting attack?",
            "question_type": "mcq",
            "options": [
                "An email asking you to confirm your password",
                "A website offering a free cracked version of popular software in exchange for disabling antivirus",
                "A colleague sharing a document via the official corporate storage system",
                "A reminder from HR to complete annual training"
            ],
            "correct_option_index": 1
        },
        {
            "question_text": "Match the bait type to its main risk",
            "question_type": "matching",
            "pairs": {
                "Unknown USB drive": "Malware infection via removable media",
                "Free movie download": "Malicious executable or bundled spyware",
                "Leaked company document link": "Credential harvesting or download of malware disguised as documents"
            }
        },
        {
            "question_text": "A stranger at a conference hands you a USB stick containing their \"portfolio and tools\" and suggests you try them on your corporate laptop. What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Plug it in but only open documents, not programs",
                "Scan it with your personal antivirus, then use it on your work device",
                "Refuse to use unknown media and instead exchange contact details or a link to their online portfolio",
                "Accept it and share it with your teammates so they can also evaluate the tools"
            ],
            "correct_option_index": 2
        }
    ],
    "Quid Pro Quo": [
        {
            "question_text": "A caller offers to upgrade your VPN software for free if you first share your login credentials so they can \"verify your account\". This is an example of which attack type?",
            "question_type": "mcq",
            "options": [
                "Baiting",
                "Quid Pro Quo",
                "Phishing",
                "Tailgating"
            ],
            "correct_option_index": 1
        },
        {
            "question_text": "Fill in the blank: Quid Pro Quo attacks are based on the idea of \"something for ______\" – the attacker offers a benefit in exchange for access or information.",
            "question_type": "fill_blank",
            "correct_answer": "something"
        },
        {
            "question_text": "A person claiming to be from \"software support\" emails you: \"We can remove annoying pop-ups from your computer. Reply with your username and password so we can log in and fix it for you.\" What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Send the credentials; they are helping you",
                "Ask them to call you and confirm they are legitimate",
                "Ignore the email and report it through the official phishing reporting process",
                "Send a different test password first to see what happens"
            ],
            "correct_option_index": 2
        },
        {
            "question_text": "Match the scenario to why it is risky",
            "question_type": "matching",
            "pairs": {
                "Free gift card survey": "Credentials harvesting disguised as a promotional survey",
                "Free license extension": "Privilege abuse by obtaining elevated access credentials",
                "Free data analysis": "Exfiltration of sensitive business data under the cover of a service"
            }
        },
        {
            "question_text": "An online \"support agent\" offers to speed up your computer if you install a remote access tool they provide. What is the best response?",
            "question_type": "scenario_mcq",
            "options": [
                "Install it only on a test machine",
                "Install it but monitor what they do",
                "Decline the offer and use only remote tools approved by your organization",
                "Accept but change your password right afterward"
            ],
            "correct_option_index": 2
        }
    ],
    "Tailgating": [
        {
            "question_text": "As you badge into a secure office area, a person carrying boxes asks you to \"hold the door\" because they forgot their badge. You do not recognize them. What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Hold the door open to be polite",
                "Let them in if they promise to go straight to reception",
                "Politely refuse and ask them to badge in themselves or check in at reception",
                "Let them in and notify security later"
            ],
            "correct_option_index": 2
        },
        {
            "question_text": "Fill in the blank: Tailgating is a physical security attack where an unauthorized person gains access by closely ______ an authorized person.",
            "question_type": "fill_blank",
            "correct_answer": "following"
        },
        {
            "question_text": "Which of the following is the BEST control to reduce tailgating risk?",
            "question_type": "mcq",
            "options": [
                "Installing stronger Wi-Fi passwords",
                "Training employees not to let strangers follow them through secure doors",
                "Allowing visitors to walk freely if they look professional",
                "Placing more trash bins near doors"
            ],
            "correct_option_index": 1
        },
        {
            "question_text": "Match the behavior to its security impact",
            "question_type": "matching",
            "pairs": {
                "Lending your access badge": "Removes accountability for access and enables misuse",
                "Propping open a secure door": "Bypasses door controls and enables tailgating by anyone",
                "Escorting a visitor": "Follows policy by maintaining oversight of non-employees"
            }
        },
        {
            "question_text": "You see someone you don't recognize tailgating into your floor behind another employee. What is the most appropriate step?",
            "question_type": "scenario_mcq",
            "options": [
                "Ignore it; the person probably belongs there",
                "Challenge them aggressively and demand ID",
                "Politely ask if they need help checking in and direct them to reception or security, then report if something feels off",
                "Follow them silently to see where they go"
            ],
            "correct_option_index": 2
        }
    ],
    "Vishing": [
        {
            "question_text": "Someone calls claiming to be from your bank’s fraud department, saying there was a suspicious transaction. They ask you to confirm your full card number and CVV over the phone. What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Provide the information so they can stop the fraud quickly",
                "Refuse, hang up, and call the bank back using the official number on your card or website",
                "Ask them to email you the details and then reply with the information",
                "Give only part of the card number to reduce the risk"
            ],
            "correct_option_index": 1
        },
        {
            "question_text": "Fill in the blank: Vishing attacks often combine caller ID spoofing with a sense of ______ to push the victim into acting without thinking.",
            "question_type": "fill_blank",
            "correct_answer": "urgency"
        },
        {
            "question_text": "Which sign is a strong indicator that a phone call might be a vishing attempt?",
            "question_type": "mcq",
            "options": [
                "The caller's number appears as an unknown number",
                "The caller insists you act immediately and refuses to let you verify the call through official channels",
                "The caller speaks with an accent",
                "The call takes place after business hours"
            ],
            "correct_option_index": 1
        },
        {
            "question_text": "Match the vishing scenario to the data being targeted",
            "question_type": "matching",
            "pairs": {
                "Fake IT support": "Network or account credentials",
                "Fake payroll": "Bank account details and personal identifiers",
                "Fake vendor": "Payment card or billing account information"
            }
        },
        {
            "question_text": "A caller says they are from your company's \"security office\" and asks you to read out the one-time passcode (OTP) you just received by SMS to \"confirm your identity.\" What is the correct action?",
            "question_type": "scenario_mcq",
            "options": [
                "Share the OTP because they already know you received it",
                "Ask them to send another OTP and share that one instead",
                "Refuse to share the OTP and report the call as suspicious",
                "Share only the first half of the OTP"
            ],
            "correct_option_index": 2
        }
    ],
    "Smishing": [
        {
            "question_text": "You receive an SMS: \"[Bank Alert] Your account is locked. Click http://secure-verify-bank-login.com to restore access.\" You were not expecting this. What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Tap the link and log in to unlock the account",
                "Reply to the SMS asking for more details",
                "Ignore the SMS and contact the bank using the official app or website you already use",
                "Forward the SMS to all friends to warn them"
            ],
            "correct_option_index": 2
        },
        {
            "question_text": "Fill in the blank: Smishing is a form of phishing that uses ______ messages as the primary channel.",
            "question_type": "fill_blank",
            "correct_answer": "SMS"
        },
        {
            "question_text": "Which of these is the LEAST risky SMS to tap on?",
            "question_type": "mcq",
            "options": [
                "A package delivery SMS with a shortened tracking link you did not request",
                "An SMS from an unknown number claiming you won a prize",
                "An SMS from your organization's official short code that you regularly receive MFA codes from, asking you to enter a code INTO the app you opened yourself",
                "An SMS claiming your social media account will be deleted in 2 hours unless you log in"
            ],
            "correct_option_index": 2
        },
        {
            "question_text": "Match the smishing example to its primary goal",
            "question_type": "matching",
            "pairs": {
                "Fake delivery notice": "card/payment details",
                "Fake bank alert": "banking credentials/OTP",
                "Fake tax refund": "identity + bank details"
            }
        },
        {
            "question_text": "An SMS appears to come from the same thread as your legitimate bank OTP codes, but this time it contains a clickable link and asks you to log in. What is the safest reaction?",
            "question_type": "scenario_mcq",
            "options": [
                "Click the link since it is in the same thread as real OTPs",
                "Ignore the SMS and instead open the official banking app directly",
                "Reply STOP to unsubscribe from messages",
                "Forward the SMS to your personal email"
            ],
            "correct_option_index": 1
        }
    ]
}


theory_content = {
    "Phishing": """
        <h3>What is Phishing?</h3>
        <p>Phishing is a cybercrime in which a target or targets are contacted by email, telephone or text message by someone posing as a legitimate institution to lure individuals into providing sensitive data such as personally identifiable information, banking and credit card details, and passwords.</p>
        <h4>Key Red Flags:</h4>
        <ul>
            <li>Generic greetings ("Dear Customer")</li>
            <li>Urgent or threatening language</li>
            <li>Suspicious attachments or links</li>
            <li>Mismatched URLs (hover over the link to check)</li>
        </ul>
    """,
    "Pretexting": """
        <h3>What is Pretexting?</h3>
        <p>Pretexting involves an attacker creating a fabricated scenario (the pretext) to steal your personal information. They might pretend to be from HR, IT support, or a vendor.</p>
        <h4>Common Pretexts:</h4>
        <ul>
            <li>"I'm from IT and need your password to fix a virus."</li>
            <li>"This is HR, we need to confirm your bank details for payroll."</li>
            <li>"I'm a delivery driver and need your address confirms."</li>
        </ul>
    """,
    "Baiting": """
        <h3>What is Baiting?</h3>
        <p>Baiting attacks use a false promise to pique a victim's greed or curiosity. Attackers lure users into a trap that steals their personal information or inflicts their systems with malware.</p>
        <h4>Examples:</h4>
        <ul>
            <li>Leaving a USB drive labeled "Confidential" or "Salary Info" in a public place.</li>
            <li>Online ads offering free expensive software (which is actually malware).</li>
        </ul>
    """,
    "Quid Pro Quo": """
        <h3>What is Quid Pro Quo?</h3>
        <p>Quid pro quo means "something for something". Attackers promise a benefit in exchange for information. This benefit is usually in the form of a service, whereas baiting usually takes the form of a good.</p>
        <h4>Scenario:</h4>
        <p>An attacker calls random extensions at a company claiming to be from tech support. Eventually, they find someone with a legitimate problem and "help" them, in the process getting them to disable firewalls or install malware.</p>
    """,
    "Tailgating": """
        <h3>What is Tailgating?</h3>
        <p>Tailgating, or piggybacking, involves an attacker seeking entry to a restricted area without proper authentication. They simply follow an authorized person through a secure door.</p>
        <h4>Prevention:</h4>
        <p>Never hold the door for people you don't recognize or who don't have a visible badge. Politely ask them to badge in themselves.</p>
    """,
    "Vishing": """
        <h3>What is Vishing?</h3>
        <p>Vishing (Voice Phishing) uses the telephone system to steal confidential information. Attackers may spoof their caller ID to look like a legitimate organization.</p>
        <h4>Defense:</h4>
        <p>If you receive a suspicious call from your bank or a company, hang up. Find the official number on the back of your card or their website and call them back directly.</p>
    """,
    "Smishing": """
        <h3>What is Smishing?</h3>
        <p>Smishing (SMS Phishing) uses text messages to trick you. These messages often contain malicious links or ask you to call a fraudulent number.</p>
        <h4>Warning Signs:</h4>
        <ul>
            <li>Messages from unknown numbers about "urgent" account issues.</li>
            <li>Texts claiming you've won a prize you didn't enter for.</li>
            <li>Requests to click a shortened link (bit.ly, etc.) to "verify" info.</li>
        </ul>
    """,
    "WiFi_Evil_Twin": """
        <h3>What is an Evil Twin Attack?</h3>
        <p>An Evil Twin is a fraudulent Wi-Fi access point that appears to be legitimate but is set up to eavesdrop on wireless communications.</p>
        <h4>How it works:</h4>
        <p>You connect to "CoffeeShop_Free_Wifi" thinking it's safe. The attacker intercepts everything you do, stealing login credentials and credit card numbers.</p>
        <p><strong>Safe Bet:</strong> Use a VPN on public Wi-Fi or stick to your mobile data.</p>
    """,
    "Honeytraps": """
        <h3>What is a Honeytrap?</h3>
        <p>A honeytrap involves an attacker attempting to start a romantic or sexual relationship with a target to steal information or for monetary gain (sextortion).</p>
        <h4>Advice:</h4>
        <p>Be wary of strangers online who move very quickly towards intimacy or ask for sensitive work information/money. Keep your digital life separate from your work life.</p>
    """,
    "Insider_Threats": """
        <h3>What are Insider Threats?</h3>
        <p>An insider threat is a security risk that originates from within the targeted organization. It doesn't have to be a current employee or officer; it can also be a former employee, contractor, or business associate.</p>
        <h4>Types:</h4>
        <ul>
            <li><strong>Malicious Insider:</strong> Someone who intentionally abuses their access for gain or revenge.</li>
            <li><strong>Negligent Insider:</strong> Someone who accidentally exposes data (e.g., losing a laptop, click a phishing link).</li>
        </ul>
    """
}

def seed_quizzes():
    app = create_app()
    with app.app_context():
        
        # Ensure categories exist
        for category_name, questions in raw_content.items():
            category = Category.query.filter_by(category_name=category_name).first()
            if not category:
                category = Category(category_name=category_name, icon='shield', description=f'{category_name} Training')
                db.session.add(category)
                db.session.commit()
                print(f"Created category: {category_name}")
            
            # Format questions for JSON storage
            formatted_questions = []
            for q in questions:
                q_data = {
                    "question": q["question_text"],
                    "type": q["question_type"]
                }
                
                if q["question_type"] in ["mcq", "scenario_mcq"]:
                    q_data["options"] = q["options"]
                    q_data["correct_answer"] = q["options"][q["correct_option_index"]]
                elif q["question_type"] == "fill_blank":
                    q_data["correct_answer"] = q["correct_answer"]
                elif q["question_type"] == "matching":
                    q_data["pairs"] = q["pairs"]
                
                formatted_questions.append(q_data)
            
            # Create or Update MicroLesson
            lesson_title = f"{category_name} Fundamentals"
            lesson = MicroLesson.query.filter_by(title=lesson_title).first()
            
            quiz_json = {"questions": formatted_questions}
            theory_text = theory_content.get(category_name, f"Learn the basics of {category_name} and how to protect yourself.")

            if lesson:
                lesson.quiz_json = quiz_json
                lesson.content_text = theory_text # Update theory content
                print(f"Updated lesson: {lesson_title}")
            else:
                lesson = MicroLesson(
                    category_id=category.category_id,
                    title=lesson_title,
                    content_text=theory_text,
                    quiz_json=quiz_json
                )
                db.session.add(lesson)
                print(f"Created lesson: {lesson_title}")
        
        db.session.commit()
        print("Quiz seeding complete!")

if __name__ == "__main__":
    seed_quizzes()
