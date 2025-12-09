from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, current_app, flash
import stripe
from app.models import User
from app import db
import os

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/upgrade')
def upgrade():
    """Render the Upgrade Page"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
        
    return render_template('upgrade.html', 
                         stripe_public_key=current_app.config['STRIPE_PUBLIC_KEY'])

@payment_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create a Stripe Checkout Session"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': 'Pro - Social Engineering Simulator',
                        'description': 'Unlimited Scenarios, Incident Response Drills, Advanced Analytics',
                    },
                    'unit_amount': 49900,  # Amount in paise (499.00 * 100)
                },
                'quantity': 1,
            }],
            mode='payment', # Use subscription if you have a recurring Product ID
            success_url=url_for('payment.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment.cancel', _external=True),
            client_reference_id=str(session['user_id']),
            metadata={
                'user_id': session['user_id']
            }
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@payment_bp.route('/payment/success')
def success():
    """Handle successful payment (UI only, logic should rely on webhook for security)"""
    # Simple direct update for demo purposes if webhooks fail locally without proper tunneling
    # In production, ONLY trust the webhook.
    session_id = request.args.get('session_id')
    
    # Optional: Verify session_id with Stripe here if not using webhooks
    
    # Ideally flash and redirect
    flash('Payment Successful! Welcome to Pro.', 'success')
    return redirect(url_for('main.dashboard'))

@payment_bp.route('/payment/cancel')
def cancel():
    flash('Payment cancelled.', 'info')
    return redirect(url_for('main.upgrade'))

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe Webhooks"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Fulfill the purchase
        user_id = session.get('client_reference_id')
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                user.subscription_tier = 'pro'
                db.session.commit()
                print(f"DEBUG: User {user.username} upgraded to PRO via Webhook.")

    return 'Success', 200
