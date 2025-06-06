from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import current_user
from sqlalchemy import or_, and_
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from models import User, Skill, SkillWanted, Message, SkillExchange, Review
from datetime import datetime

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page for logged out users, dashboard for logged in users"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/how-it-works')
def how_it_works():
    """How SkillSwap works page"""
    return render_template('how_it_works.html')

@app.route('/dashboard')
@require_login
def dashboard():
    """Dashboard showing active requests and recent activity"""
    # Get user's active exchanges
    active_exchanges = SkillExchange.query.filter(
        or_(
            and_(SkillExchange.requester_id == current_user.id, SkillExchange.status.in_(['pending', 'accepted'])),
            and_(SkillExchange.provider_id == current_user.id, SkillExchange.status.in_(['pending', 'accepted']))
        )
    ).order_by(SkillExchange.created_at.desc()).all()
    
    # Get recent messages
    recent_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).limit(5).all()
    
    # Get completed exchanges
    completed_exchanges = SkillExchange.query.filter(
        or_(
            and_(SkillExchange.requester_id == current_user.id, SkillExchange.status == 'completed'),
            and_(SkillExchange.provider_id == current_user.id, SkillExchange.status == 'completed')
        )
    ).order_by(SkillExchange.completed_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         active_exchanges=active_exchanges,
                         recent_messages=recent_messages,
                         completed_exchanges=completed_exchanges)

@app.route('/profile')
@require_login
def profile():
    """View current user's profile"""
    skills_offered = Skill.query.filter_by(user_id=current_user.id).all()
    skills_wanted = SkillWanted.query.filter_by(user_id=current_user.id).all()
    reviews = Review.query.filter_by(reviewee_id=current_user.id).order_by(Review.created_at.desc()).all()
    
    return render_template('profile.html', 
                         user=current_user,
                         skills_offered=skills_offered,
                         skills_wanted=skills_wanted,
                         reviews=reviews)

@app.route('/profile/edit', methods=['GET', 'POST'])
@require_login
def edit_profile():
    """Edit current user's profile"""
    if request.method == 'POST':
        # Update basic profile info
        current_user.bio = request.form.get('bio', '')
        current_user.location = request.form.get('location', '')
        current_user.contact_info = request.form.get('contact_info', '')
        
        # Handle skills offered
        skills_offered = request.form.getlist('skills_offered[]')
        skills_descriptions = request.form.getlist('skills_descriptions[]')
        skills_categories = request.form.getlist('skills_categories[]')
        skills_levels = request.form.getlist('skills_levels[]')
        
        # Delete existing skills and add new ones
        Skill.query.filter_by(user_id=current_user.id).delete()
        for i, skill_name in enumerate(skills_offered):
            if skill_name.strip():
                skill = Skill(
                    user_id=current_user.id,
                    name=skill_name.strip(),
                    description=skills_descriptions[i] if i < len(skills_descriptions) else '',
                    category=skills_categories[i] if i < len(skills_categories) else '',
                    level=skills_levels[i] if i < len(skills_levels) else 'Beginner'
                )
                db.session.add(skill)
        
        # Handle skills wanted
        skills_wanted = request.form.getlist('skills_wanted[]')
        skills_wanted_descriptions = request.form.getlist('skills_wanted_descriptions[]')
        skills_wanted_categories = request.form.getlist('skills_wanted_categories[]')
        
        # Delete existing wanted skills and add new ones
        SkillWanted.query.filter_by(user_id=current_user.id).delete()
        for i, skill_name in enumerate(skills_wanted):
            if skill_name.strip():
                skill_wanted = SkillWanted(
                    user_id=current_user.id,
                    name=skill_name.strip(),
                    description=skills_wanted_descriptions[i] if i < len(skills_wanted_descriptions) else '',
                    category=skills_wanted_categories[i] if i < len(skills_wanted_categories) else ''
                )
                db.session.add(skill_wanted)
        
        current_user.updated_at = datetime.now()
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    skills_offered = Skill.query.filter_by(user_id=current_user.id).all()
    skills_wanted = SkillWanted.query.filter_by(user_id=current_user.id).all()
    
    return render_template('edit_profile.html', 
                         user=current_user,
                         skills_offered=skills_offered,
                         skills_wanted=skills_wanted)

@app.route('/search')
@require_login
def search():
    """Search for users by skills"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    users = []
    if query or category:
        # Search in skills offered
        skill_query = Skill.query
        if query:
            skill_query = skill_query.filter(Skill.name.ilike(f'%{query}%'))
        if category:
            skill_query = skill_query.filter(Skill.category == category)
        
        # Get unique users from skills
        skill_users = skill_query.join(User).filter(User.id != current_user.id).all()
        user_ids = set([skill.user_id for skill in skill_users])
        users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    
    # Get all categories for filter
    categories = db.session.query(Skill.category).filter(Skill.category.isnot(None)).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('search.html', 
                         users=users, 
                         query=query, 
                         category=category,
                         categories=categories)

@app.route('/user/<user_id>')
@require_login
def user_profile(user_id):
    """View another user's profile"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return redirect(url_for('profile'))
    
    skills_offered = Skill.query.filter_by(user_id=user_id).all()
    skills_wanted = SkillWanted.query.filter_by(user_id=user_id).all()
    reviews = Review.query.filter_by(reviewee_id=user_id).order_by(Review.created_at.desc()).limit(10).all()
    
    return render_template('user_profile.html', 
                         user=user,
                         skills_offered=skills_offered,
                         skills_wanted=skills_wanted,
                         reviews=reviews)

@app.route('/messages')
@require_login
def messages():
    """View all conversations"""
    # Get all conversations (unique sender/recipient pairs)
    sent_messages = db.session.query(Message.recipient_id).filter_by(sender_id=current_user.id).distinct().all()
    received_messages = db.session.query(Message.sender_id).filter_by(recipient_id=current_user.id).distinct().all()
    
    contact_ids = set()
    for msg in sent_messages:
        contact_ids.add(msg[0])
    for msg in received_messages:
        contact_ids.add(msg[0])
    
    conversations = []
    for contact_id in contact_ids:
        contact = User.query.get(contact_id)
        if contact:
            # Get latest message in conversation
            latest_message = Message.query.filter(
                or_(
                    and_(Message.sender_id == current_user.id, Message.recipient_id == contact_id),
                    and_(Message.sender_id == contact_id, Message.recipient_id == current_user.id)
                )
            ).order_by(Message.created_at.desc()).first()
            
            # Count unread messages
            unread_count = Message.query.filter_by(
                sender_id=contact_id,
                recipient_id=current_user.id,
                is_read=False
            ).count()
            
            conversations.append({
                'contact': contact,
                'latest_message': latest_message,
                'unread_count': unread_count
            })
    
    # Sort by latest message time
    conversations.sort(key=lambda x: x['latest_message'].created_at if x['latest_message'] else datetime.min, reverse=True)
    
    return render_template('messages.html', conversations=conversations)

@app.route('/conversation/<user_id>')
@require_login
def conversation(user_id):
    """View conversation with a specific user"""
    contact = User.query.get_or_404(user_id)
    
    # Get all messages in conversation
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.recipient_id == user_id),
            and_(Message.sender_id == user_id, Message.recipient_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    Message.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    return render_template('conversation.html', contact=contact, messages=messages)

@app.route('/send_message/<user_id>', methods=['POST'])
@require_login
def send_message(user_id):
    """Send a message to another user"""
    recipient = User.query.get_or_404(user_id)
    content = request.form.get('content', '').strip()
    subject = request.form.get('subject', '').strip()
    
    if not content:
        flash('Message content cannot be empty.', 'error')
        return redirect(url_for('conversation', user_id=user_id))
    
    message = Message(
        sender_id=current_user.id,
        recipient_id=user_id,
        subject=subject,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    flash('Message sent successfully!', 'success')
    return redirect(url_for('conversation', user_id=user_id))

@app.route('/request_exchange/<user_id>', methods=['POST'])
@require_login
def request_exchange(user_id):
    """Request a skill exchange with another user"""
    provider = User.query.get_or_404(user_id)
    skill_requested = request.form.get('skill_requested', '').strip()
    skill_offered = request.form.get('skill_offered', '').strip()
    description = request.form.get('description', '').strip()
    
    if not skill_requested or not skill_offered:
        flash('Both requested and offered skills are required.', 'error')
        return redirect(url_for('user_profile', user_id=user_id))
    
    exchange = SkillExchange(
        requester_id=current_user.id,
        provider_id=user_id,
        skill_requested=skill_requested,
        skill_offered=skill_offered,
        description=description
    )
    db.session.add(exchange)
    db.session.commit()
    
    # Send notification message
    message = Message(
        sender_id=current_user.id,
        recipient_id=user_id,
        subject=f"Skill Exchange Request: {skill_requested}",
        content=f"{current_user.get_full_name()} has requested to exchange '{skill_offered}' for '{skill_requested}'. {description}"
    )
    db.session.add(message)
    db.session.commit()
    
    flash('Exchange request sent successfully!', 'success')
    return redirect(url_for('user_profile', user_id=user_id))

@app.route('/exchange/<int:exchange_id>/respond', methods=['POST'])
@require_login
def respond_to_exchange(exchange_id):
    """Accept or decline an exchange request"""
    exchange = SkillExchange.query.get_or_404(exchange_id)
    
    if exchange.provider_id != current_user.id:
        flash('You are not authorized to respond to this exchange.', 'error')
        return redirect(url_for('dashboard'))
    
    action = request.form.get('action')
    if action == 'accept':
        exchange.status = 'accepted'
        flash('Exchange request accepted!', 'success')
    elif action == 'decline':
        exchange.status = 'cancelled'
        flash('Exchange request declined.', 'info')
    
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/exchange/<int:exchange_id>/complete', methods=['POST'])
@require_login
def complete_exchange(exchange_id):
    """Mark an exchange as completed"""
    exchange = SkillExchange.query.get_or_404(exchange_id)
    
    if exchange.requester_id != current_user.id and exchange.provider_id != current_user.id:
        flash('You are not authorized to complete this exchange.', 'error')
        return redirect(url_for('dashboard'))
    
    exchange.status = 'completed'
    exchange.completed_at = datetime.now()
    db.session.commit()
    
    flash('Exchange marked as completed! You can now leave a review.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/reviews')
@require_login
def reviews():
    """View all reviews for current user"""
    reviews = Review.query.filter_by(reviewee_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('reviews.html', reviews=reviews)

@app.route('/exchange/<int:exchange_id>/review', methods=['POST'])
@require_login
def leave_review(exchange_id):
    """Leave a review for a completed exchange"""
    exchange = SkillExchange.query.get_or_404(exchange_id)
    
    if exchange.status != 'completed':
        flash('You can only review completed exchanges.', 'error')
        return redirect(url_for('dashboard'))
    
    if exchange.requester_id != current_user.id and exchange.provider_id != current_user.id:
        flash('You are not authorized to review this exchange.', 'error')
        return redirect(url_for('dashboard'))
    
    # Determine who is being reviewed
    if exchange.requester_id == current_user.id:
        reviewee_id = exchange.provider_id
    else:
        reviewee_id = exchange.requester_id
    
    # Check if review already exists
    existing_review = Review.query.filter_by(
        exchange_id=exchange_id,
        reviewer_id=current_user.id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this exchange.', 'error')
        return redirect(url_for('dashboard'))
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        flash('Please provide a valid rating (1-5 stars).', 'error')
        return redirect(url_for('dashboard'))
    
    review = Review(
        exchange_id=exchange_id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('403.html', error_message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('403.html', error_message="Internal server error"), 500
