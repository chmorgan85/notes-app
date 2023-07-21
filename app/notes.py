import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db


bp = Blueprint('notes', __name__)



@bp.route('/')
@login_required
def index():
    db = get_db()
    notes = db.execute(
        'SELECT *'
        ' FROM note n'
        ' WHERE n.author_id = ?',
        (g.user['id'],)
    ).fetchall()
    
    return render_template('notes/index.html', notes=notes)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        db = get_db()
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db.execute(
                    'INSERT INTO note (title, body, author_id) VALUES (?, ?, ?)',
                    (title, body, g.user['id'])
                )
            db.commit()

            return redirect(url_for('notes.index'))

    return render_template('notes/create.html')


def get_note(id):
    note = get_db().execute(
        'SELECT *'
        ' FROM note n'
        ' WHERE n.id = ?',
        (id,)
    ).fetchone()

    if note is None:
        abort(404, f"Note id {id} doesn't exist.")
    
    if note['author_id'] != g.user['id']:
        abort(403)
    
    return note


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    note = get_note(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE note SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('notes.index'))
        
    return render_template('notes/update.html', note=note)
        

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_note(id)
    db = get_db()
    db.execute('DELETE FROM note WHERE id = ?', (id,))
    db.commit()

    return redirect(url_for('notes.index'))

