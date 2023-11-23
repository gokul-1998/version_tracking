from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Dashboard %r>' % self.id
    
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboard.id'), nullable=False)
    dashboard = db.relationship('Dashboard', backref=db.backref('pages', lazy=True))

    def __repr__(self):
        return '<Page %r>' % self.id

class Widget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    page = db.relationship('Page', backref=db.backref('widgets', lazy=True))

    def __repr__(self):
        return '<Widget %r>' % self.id
    
class DashboardVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboard.id'), nullable=False)
    dashboard = db.relationship('Dashboard', backref=db.backref('versions', lazy=True))
    version = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<DashboardVersion %r>' % self.id
    
with app.app_context():
  db.create_all()

def add_dashboard(name, description):
    dashboard = Dashboard(name=name, description=description)
    db.session.add(dashboard)
    db.session.commit()

def add_dashboard_version(dashboard_id, version, created_at):
    dashboard_version = DashboardVersion(dashboard_id=dashboard_id, version=version, created_at=created_at)
    db.session.add(dashboard_version)
    db.session.commit()

def add_page(name, dashboard_id):
    page = Page(name=name, dashboard_id=dashboard_id)
    db.session.add(page)
    db.session.commit()

def add_widget(name, page_id):
    widget = Widget(name=name, page_id=page_id)
    db.session.add(widget)
    db.session.commit()
with app.app_context():  
  if Dashboard.query.count() == 0:
      add_dashboard('Dashboard 1', 'This is the first dashboard')
      add_dashboard_version(1, 1, datetime.now())
      add_page('Page 1', 1)
      add_widget('Widget 1', 1)
      add_widget('Widget 2', 1)
      add_page('Page 2', 1)
      add_widget('Widget 3', 2)
      add_widget('Widget 4', 2)

@app.route('/')
def index():
    db_version=DashboardVersion.query.filter_by(id=1).first()
    print(db_version)
    return render_template('index.html',db_version=db_version)



if __name__ == '__main__':
    app.run(debug=True)