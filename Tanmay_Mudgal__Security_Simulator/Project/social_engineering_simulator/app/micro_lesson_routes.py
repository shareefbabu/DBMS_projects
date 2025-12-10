from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from app import db
from app.models import MicroLesson, AssignedLesson, User
from datetime import datetime

micro_lesson_bp = Blueprint('micro_lesson', __name__)

@micro_lesson_bp.route('/lesson/<int:lesson_id>')
def view_lesson(lesson_id):
    """Display the micro-lesson content and quiz"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
        
    user_id = session['user_id']
    lesson = MicroLesson.query.get_or_404(lesson_id)
    
    # Check if assigned
    assignment = AssignedLesson.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    
    # If not assigned but user is accessing (maybe via direct link), assign it
    if not assignment:
        assignment = AssignedLesson(
            user_id=user_id,
            lesson_id=lesson_id,
            status='in_progress'
        )
        db.session.add(assignment)
        db.session.commit()
    elif assignment.status == 'pending':
        assignment.status = 'in_progress'
        db.session.commit()
        
    return render_template('micro_lesson_player.html', lesson=lesson, assignment=assignment)

@micro_lesson_bp.route('/submit-lesson/<int:assignment_id>', methods=['POST'])
def submit_lesson_quiz(assignment_id):
    """Process quiz submission and update completion"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    assignment = AssignedLesson.query.get_or_404(assignment_id)
    if assignment.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    answers = data.get('answers', {})
    
    lesson = assignment.lesson
    quiz_data = lesson.quiz_json
    questions = quiz_data.get('questions', [])
    
    correct_count = 0
    total_questions = len(questions)
    
    for i, question in enumerate(questions):
        question_type = question.get('type', 'mcq')
        
        if question_type in ['mcq', 'scenario_mcq']:
            user_answer = answers.get(f'q{i}')
            if user_answer == question['correct_answer']:
                correct_count += 1
                
        elif question_type == 'fill_blank':
            user_answer = answers.get(f'q{i}')
            if user_answer:
                # Case-insensitive, whitespace-stripped comparison
                if user_answer.lower().strip() == question['correct_answer'].lower().strip():
                    correct_count += 1
                    
        elif question_type == 'matching':
            # Check all pairs
            all_correct = True
            pairs = question.get('pairs', {})
            # Frontend sends keys as "q{question_index}_{pair_index}"
            # But wait, our seed script doesn't assign indices to pairs.
            # Frontend iterates pairs.items().
            # We need to match frontend submission format.
            # Frontend JS collects: matches[q{i}_{j}] = selected_value
            
            # Let's reconstruct logic.
            # Frontend sends: answers = { 'q{i}_{k}': 'value' } where k is index of pair.
            # We iterate through the correct pairs (sorted keys maybe?) to match indices.
            
            # Better approach: Iterate keys in pairs.
            # Since frontend iterates pairs.items(), order is preserved (Python 3.7+ dicts are ordered).
            current_pairs = list(pairs.items())
            for pair_idx, (key, correct_val) in enumerate(current_pairs):
                user_val = answers.get(f'q{i}_{pair_idx}')
                if user_val != correct_val:
                    all_correct = False
                    break
            
            if all_correct and len(pairs) > 0:
                correct_count += 1
        
    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    # Update assignment
    assignment.status = 'completed'
    assignment.quiz_score = score
    assignment.completed_at = datetime.utcnow()
    
    # Award points to user (e.g., 50 points for completing a lesson)
    user = User.query.get(session['user_id'])
    points_earned = 50
    user.total_score += points_earned
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'score': score,
        'points_earned': points_earned,
        'new_total': user.total_score
    })
