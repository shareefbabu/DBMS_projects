import json
import random
from app import create_app, db
from app.models import Scenario

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
            "correct_option_index": 2,
            "explanation": "Never trust links in unexpected emails. Going directly to the official URL ensures you aren't landing on a spoofed page. The sender domain 'security-it-updates.com' is not your official company domain."
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
            "correct_option_index": 1,
            "explanation": "SPF and DKIM are specific email authentication protocols. Failure means the email server could not verify that the sender is unauthorized, significantly increasing the risk of spoofing."
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
            "correct_option_index": 2,
            "explanation": "Legitimate IT support will NEVER ask for your password. Attackers use confidence and jargon (pretexting) to trick you. Always verify by calling back on a known official number."
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
            "correct_option_index": 2,
            "explanation": "Urgency and breaking protocol (using personal email) are classic signs of CEO Fraud or impersonation. Always verify out-of-band before releasing sensitive data."
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
            "correct_option_index": 2,
            "explanation": "A USB drive found in a public area is likely a 'bait' loaded with malware. Plugging it in triggers an auto-run attack. Handing it to security safely mitigates the threat."
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
            "correct_option_index": 2,
            "explanation": "Untrusted media is a primary vector for air-gapped network compromise. Never plug unknown hardware into your machine. Digital transfer allows for network-level scanning."
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
            "correct_option_index": 1,
            "explanation": "Quid Pro Quo means 'something for something'. The attacker offers a benefit (VPN upgrade) in exchange for information (credentials)."
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
            "correct_option_index": 2,
            "explanation": "Unsolicited offers of help are suspicious. Legitimate support tickets originate from you. Sharing credentials allows them to install the very malware they claim to fix."
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
            "correct_option_index": 2,
            "explanation": "Remote Access Trojans (RATs) are often disguised as support tools. Following company software policy protects you from unauthorized remote control."
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
            "correct_option_index": 2,
            "explanation": "Attackers exploit courtesy to bypass physical security. 'Piggybacking' or 'Tailgating' is prevented by requiring every individual to badge in."
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
            "correct_option_index": 1,
            "explanation": "Technical controls (like mantraps) help, but human awareness is the most critical defense against social engineering like tailgating."
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
            "correct_option_index": 2,
            "explanation": "Challenge protocol should be polite but firm. Asking 'Can I help you find someone?' often deters intruders. Reporting to security is the safe escalation."
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
            "correct_option_index": 1,
            "explanation": "Bank fraud departments already have your card number. Asking for the CVV is a major red flag. Hanging up and dialing the official number verifies the call."
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
            "correct_option_index": 1,
            "explanation": "Attackers create false urgency to bypass critical thinking. Refusing verification is a hallmark of a scam."
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
            "correct_option_index": 2,
            "explanation": "OTPs are for YOU to authenticate to a system, never for a human to authenticate you. Sharing an OTP usually allows the attacker to bypass MFA on your account."
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
            "correct_option_index": 2,
            "explanation": "This text uses urgency ('locked') and a look-alike domain. Using the official app avoids the malicious link entirely."
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
            "question_text": "An SMS appears to come from the same thread as your legitimate bank OTP codes, but this time it contains a clickable link and asks you to log in. What is the safest reaction?",
            "question_type": "scenario_mcq",
            "options": [
                "Click the link since it is in the same thread as real OTPs",
                "Ignore the SMS and instead open the official banking app directly",
                "Reply STOP to unsubscribe from messages",
                "Forward the SMS to your personal email"
            ],
            "correct_option_index": 1,
            "explanation": "SMS 'Threading' is unreliable; attackers can spoof the Sender ID to make malicious texts appear in legitimate threads. Always verify independently."
        }
    ],
    "WiFi_Evil_Twin": [
        {
            "question_text": "At a café, you see two Wi-Fi networks: \"Cafe_WiFi\" and \"Cafe_WiFi_Free\". The staff only mentioned one network named \"Cafe_WiFi\". What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Connect to the one with stronger signal",
                "Connect to both and see which one works better",
                "Ask the staff which network is legitimate and connect only to that, avoiding sensitive logins on public Wi-Fi",
                "Assume both are safe because they include the café name"
            ],
            "correct_option_index": 2,
            "explanation": "An 'Evil Twin' is a rogue access point mimicking a legitimate one. Connecting to it allows the attacker to intercept your traffic."
        },
        {
            "question_text": "Which practice best protects you when using public Wi-Fi?",
            "question_type": "mcq",
            "options": [
                "Logging into all accounts quickly and logging out",
                "Using a trusted VPN and avoiding access to highly sensitive services if possible",
                "Turning off your device firewall",
                "Sharing the network password with others so everyone uses the same one"
            ],
            "correct_option_index": 1,
            "explanation": "A VPN encrypts your traffic, protecting it even if the Wi-Fi network itself is compromised or unencrypted."
        },
        {
            "question_text": "You connect to hotel Wi-Fi and a page pops up asking for your corporate email and password to \"synchronize work access.\" What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Enter your details to get better access",
                "Use only your room number and name because that is safer",
                "Close the page and access corporate resources only through your VPN and official login pages",
                "Try another browser and see if the page changes"
            ],
            "correct_option_index": 2,
            "explanation": "Wi-Fi portals should only ask for room numbers or a simple passcode. Asking for corporate credentials is a clear credential harvesting attack."
        }
    ],
    "Honeytraps": [
         {
            "question_text": "Someone you met on a social networking site gradually builds a friendly relationship and then asks you to send internal project documents to \"help them understand your work better.\" What should you do?",
            "question_type": "scenario_mcq",
            "options": [
                "Send only non-confidential documents",
                "Send everything because they seem trustworthy after weeks of chatting",
                "Refuse and explain you cannot share work documents, then consider reporting the request",
                "Ask them to promise not to share the files"
            ],
            "correct_option_index": 2,
            "explanation": "Honeytraps exploit emotional connections. Attackers groom victims over time before asking for sensitive data. Policy should always override personal trust."
        },
        {
            "question_text": "Which sign is a red flag that an online relationship might be part of a honeytrap?",
            "question_type": "mcq",
            "options": [
                "They never ask about your job",
                "They quickly move the conversation toward secrets about your work or finances",
                "They like the same music as you",
                "They live in the same city"
            ],
            "correct_option_index": 1,
            "explanation": "Accelerating intimacy and shifting focus to confidential topics are key indicators of a targeted social engineering operation."
        },
        {
            "question_text": "An online acquaintance suggests meeting in person and asks you to bring your work laptop so they can \"see your cool tools.\" What is the best response?",
            "question_type": "scenario_mcq",
            "options": [
                "Bring the laptop but avoid logging in",
                "Decline to bring any work devices or data and follow company policy about external meetings",
                "Bring only a USB with some tools",
                "Share screenshots instead of live access"
            ],
            "correct_option_index": 1,
            "explanation": "Physical access to assets is high risk. Bringing corporate devices to unvetted meetings exposes them to theft or compromise."
        }
    ],
    "Insider_Threats": [
        {
            "question_text": "You notice a colleague downloading large amounts of customer data to a personal USB drive without a clear business reason. What is the most appropriate action?",
            "question_type": "scenario_mcq",
            "options": [
                "Ignore it because they probably know what they are doing",
                "Ask them for a copy of the data for yourself",
                "Report the behavior through the company’s confidential reporting or security channel",
                "Post about it on social media to warn others"
            ],
            "correct_option_index": 2,
            "explanation": "Data exfiltration is a major insider threat. 'See something, say something' helps security teams investigate potential data theft early."
        },
        {
            "question_text": "Which of the following is an example of a negligent insider threat?",
            "question_type": "mcq",
            "options": [
                "Intentionally selling company secrets to a competitor",
                "Accidentally sending a sensitive spreadsheet to the wrong external email address",
                "Deliberately destroying logs to hide activity",
                "Creating a hidden backdoor account in production"
            ],
            "correct_option_index": 1,
            "explanation": "Insider threats aren't always malicious. Negligence (carelessness) causes significantly more incidents than malice."
        },
        {
            "question_text": "A coworker asks you to share your login so they can \"quickly run a report\" while their own account is under review. What is the correct response?",
            "question_type": "scenario_mcq",
            "options": [
                "Share your credentials temporarily to help them",
                "Log in for them and let them use your session",
                "Decline, explain that sharing credentials is prohibited, and suggest they work with IT or their manager",
                "Give them your old password instead of your current one"
            ],
            "correct_option_index": 2,
            "explanation": "Credential sharing destroys audit trails and accountability. If they perform a malicious action under your ID, you are liable."
        }
    ]
}

def seed_scenarios():
    app = create_app()
    with app.app_context():
        
        for category, questions in raw_content.items():
            print(f"Seeding {category}...")
            for q in questions:
                # Check if exists
                exists = Scenario.query.filter_by(scenario_description=q['question_text']).first()
                if exists:
                    # Update options AND correct_answer if added but existing
                    exists.options_json = q['options']
                    exists.correct_answer = q['options'][q['correct_option_index']]
                    continue
                
                # New scenario
                scenario = Scenario(
                    scenario_type=category,
                    difficulty_level='medium', # Default
                    scenario_description=q['question_text'],
                    correct_answer=q['options'][q['correct_option_index']], # Store the TEXT of the correct answer
                    options_json=q['options'],
                    explanation=q.get('explanation', "Correct! Good security practice.") # Use specific explanation
                )
                db.session.add(scenario)
        
        db.session.commit()
        print("Scenario seeding complete!")

if __name__ == "__main__":
    seed_scenarios()
