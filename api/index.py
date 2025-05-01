from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from collections import Counter
from datetime import datetime
import os

#db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'tracker.db')
#app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath(db_path)}'


#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app = Flask(__name__)

# Set DB path (adjusted for Vercel deployment)
db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'tracker.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath(db_path)}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ------------------- MODELS -------------------

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, index=True)  # Indexed
    major = db.Column(db.String(100))
    applications = db.relationship('Application', backref='user', cascade='all, delete')

class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)  # Indexed
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    headquarters = db.Column(db.String(100))
    applications = db.relationship('Application', backref='company', cascade='all, delete')

class Status(db.Model):
    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50))

class Application(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), index=True)  # Indexed
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), index=True)  # Indexed
    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'), index=True)  # Indexed
    position_title = db.Column(db.String(100))
    applied_date = db.Column(db.String(10), index=True)  # Indexed
    response_date = db.Column(db.String(10))
    link_to_posting = db.Column(db.String(255))

    status = db.relationship('Status')


# ------------------- DATABASE INIT -------------------

with app.app_context():
    db.create_all()

    if not User.query.first():
        db.session.add_all([
            User(name='Alice Johnson', email='alice@example.com', major='CS'),
            User(name='Bob Smith', email='bob@example.com', major='Data Science'),
        ])
        db.session.add_all([
            Company(name='Google', industry='Tech', size='Large', headquarters='Mountain View'),
            Company(name='Dropbox', industry='Tech', size='Medium', headquarters='San Francisco'),
        ])
        db.session.add_all([
            Status(status_name='Applied'),
            Status(status_name='Interviewed'),
            Status(status_name='Rejected'),
            Status(status_name='Offer'),
        ])
        db.session.commit()

# ------------------- ROUTES -------------------

@app.route('/', methods=['GET'])
def index():
    selected_user_id = request.args.get('user_id', type=int)
    users = User.query.all()

    if selected_user_id:
        applications = Application.query.filter_by(user_id=selected_user_id).all()
    else:
        applications = Application.query.all()

    return render_template('index.html', applications=applications, users=users, selected_user_id=selected_user_id)


@app.route('/add', methods=['GET', 'POST'])
def add_application():
    if request.method == 'POST':
        new_app = Application(
            user_id=request.form['user_id'],
            company_id=request.form['company_id'],
            status_id=request.form['status_id'],
            position_title=request.form['position_title'],
            applied_date=request.form['applied_date'],
            response_date=request.form['response_date'],
            link_to_posting=request.form['link_to_posting']
        )
        db.session.add(new_app)
        db.session.commit()
        return redirect(url_for('index'))

    users = User.query.all()
    companies = Company.query.all()
    statuses = Status.query.all()
    return render_template('add_application.html', users=users, companies=companies, statuses=statuses)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_application(id):
    app_data = Application.query.get(id)

    if request.method == 'POST':
        app_data.user_id = request.form['user_id']
        app_data.company_id = request.form['company_id']
        app_data.status_id = request.form['status_id']
        app_data.position_title = request.form['position_title']
        app_data.applied_date = request.form['applied_date']
        app_data.response_date = request.form['response_date']
        app_data.link_to_posting = request.form['link_to_posting']
        db.session.commit()
        return redirect(url_for('index'))

    users = User.query.all()
    companies = Company.query.all()
    statuses = Status.query.all()
    return render_template('edit_application.html', app_data=app_data, users=users, companies=companies, statuses=statuses)


@app.route('/delete/<int:id>')
def delete_application(id):
    app_data = Application.query.get(id)
    db.session.delete(app_data)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/users', methods=['GET', 'POST'])
def view_users():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        major = request.form['major']
        new_user = User(name=name, email=email, major=major)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('view_users'))

    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('view_users'))


@app.route('/companies', methods=['GET', 'POST'])
def view_companies():
    if request.method == 'POST':
        name = request.form['name']
        industry = request.form['industry']
        size = request.form['size']
        headquarters = request.form['headquarters']
        new_company = Company(name=name, industry=industry, size=size, headquarters=headquarters)
        db.session.add(new_company)
        db.session.commit()
        return redirect(url_for('view_companies'))

    companies = Company.query.all()
    return render_template('companies.html', companies=companies)


@app.route('/delete_company/<int:company_id>')
def delete_company(company_id):
    company = Company.query.get(company_id)
    db.session.delete(company)
    db.session.commit()
    return redirect(url_for('view_companies'))

# ------------------- REPORT ROUTE -------------------

@app.route('/report', methods=['GET', 'POST'])
def report():
    statuses = Status.query.all()
    applications = []
    summary = {}

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        status_id = request.form.get('status_id')

        query = """
        SELECT a.*, s.status_name, c.name as company_name
        FROM application a
        JOIN status s ON a.status_id = s.status_id
        JOIN company c ON a.company_id = c.company_id
        WHERE (:status_id IS NULL OR a.status_id = :status_id)
          AND (:start_date IS NULL OR a.applied_date >= :start_date)
          AND (:end_date IS NULL OR a.applied_date <= :end_date)
        """

        params = {
            'status_id': status_id if status_id else None,
            'start_date': start_date if start_date else None,
            'end_date': end_date if end_date else None,
        }

        result = db.session.execute(text(query), params)
        applications = result.fetchall()

        total = len(applications)
        offer_count = 0
        reject_count = 0
        response_days = []
        company_counter = Counter()

        for app in applications:
            status = app.status_name
            if status.lower() == 'offer':
                offer_count += 1
            elif status.lower() == 'rejected':
                reject_count += 1

            if app.applied_date and app.response_date:
                try:
                    d1 = datetime.strptime(app.applied_date, '%Y-%m-%d')
                    d2 = datetime.strptime(app.response_date, '%Y-%m-%d')
                    delta = (d2 - d1).days
                    if delta >= 0:
                        response_days.append(delta)
                except Exception:
                    pass

            company_counter[app.company_name] += 1

        summary = {
            'total_applications': total,
            'offer_rate': f"{(offer_count / total * 100):.1f}%" if total else "N/A",
            'rejection_rate': f"{(reject_count / total * 100):.1f}%" if total else "N/A",
            'avg_response_time': f"{(sum(response_days) / len(response_days)):.1f} days" if response_days else "N/A",
            'most_applied_company': company_counter.most_common(1)[0][0] if company_counter else "N/A"
        }

    return render_template('report.html', applications=applications, statuses=statuses, summary=summary)


# ------------------- RUN APP -------------------

if __name__ == '__main__':
   app.run(debug=True)

#app=app
