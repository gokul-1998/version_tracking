from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
import json

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Dashboard %r>' % self.id
    
    def get_dashboard(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
    
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboard.id'), nullable=False)
    # above line is to delete all pages when dashboard is deleted
    # the cascade will not work if we use db.drop_all() to delete the tables
    # if i delete a page i want to delete all the widgets in that page
    # to do that we need to add ondelete="Cascade" in the foreign key
    # refer: https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete
    page_widget= db.relationship('Widget',cascade = "all,delete", backref=db.backref('widget_page', lazy=True))
    dashboard = db.relationship('Dashboard', backref=db.backref('pages', lazy=True))

    def __repr__(self):
        return '<Page %r>' % self.id
    
    def get_page(self):
        return {
            'id': self.id,
            'name': self.name,
            'dashboard_id': self.dashboard_id
        }

class Widget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id',ondelete='Cascade'), nullable=False)
    page = db.relationship('Page',cascade = "all,delete", backref=db.backref('widgets', lazy=True))

    def __repr__(self):
        return '<Widget %r>' % self.id
    
    def get_widget(self):
        return {
            'id': self.id,
            'name': self.name,
            'page_id': self.page_id
        }
    
class DashboardVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboard.id',ondelete="Cascade"), nullable=False)
    
    dashboard = db.relationship('Dashboard',cascade = "all,delete", backref=db.backref('versions', lazy=True))
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
    #   add_page('Page 1', 1)
    #   add_widget('Widget 1', 1)
    #   add_widget('Widget 2', 1)
    #   add_page('Page 2', 1)
    #   add_widget('Widget 3', 2)
    #   add_widget('Widget 4', 2)

def get_dashboard(id,filename):
    resp={}
    db_data= DashboardVersion.query.filter_by(id=id).first()
    
    temp=db_data.dashboard.get_dashboard()
    resp['dashboard']=temp
    resp['dashboard']['pages']=[page.get_page() for page in db_data.dashboard.pages]
    for page in resp['dashboard']['pages']:
        page['widgets']=[widget.get_widget() for widget in Widget.query.filter_by(page_id=page['id']).all()]
    

    print(resp)
    # to write to json file
    with open(f'versions/{filename}.json', 'w') as outfile:
        json.dump(resp, outfile)

with app.app_context():
    get_dashboard(1,"v2")

@app.route('/')
def index():
    db_version=DashboardVersion.query.filter_by(id=1).first()
    print(db_version)
    return render_template('index.html',db_version=db_version)

@app.route('/add_page/<int:dashboard_id>', methods=['GET', 'POST'])
def add_page_route(dashboard_id):
   if request.method == 'POST':
      name = request.form['name']
      add_page(name, dashboard_id)
      return redirect(url_for('index'))
   return render_template('add_page.html',dashboard_id=dashboard_id)

@app.route('/add_widget/<int:page_id>', methods=['GET', 'POST'])
def add_widget_route(page_id):
   if request.method == 'POST':
      name = request.form['name']
      add_widget(name, page_id)
      return redirect(url_for('index'))
   return render_template('add_widget.html',page_id=page_id)

@app.route('/delete_page/<int:id>', methods=['GET', 'POST'])
def delete_page(id):
    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_widget/<int:id>', methods=['GET', 'POST'])
def delete_widget(id):
    widget = Widget.query.get_or_404(id)
    db.session.delete(widget)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_page/<int:id>', methods=['GET', 'POST'])
def update_page(id):
    page = Page.query.get_or_404(id)
    if request.method == 'POST':
        page.name = request.form['name']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_page.html',page=page)

@app.route('/update_widget/<int:id>', methods=['GET', 'POST'])
def update_widget(id):
    widget = Widget.query.get_or_404(id)
    if request.method == 'POST':
        widget.name = request.form['name']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_widget.html',widget=widget)
import os
@app.route("/versions")
def get_all_versions():
    version_files = os.listdir('versions')
    versions = []

    for filename in version_files:
        with open(os.path.join('versions', filename)) as json_file:
            data = json.load(json_file)
            versions.append(data)

    return render_template('version.html', versions=versions)

@app.route("/versions/<string:id>")
def get_version(id):
    with open(os.path.join('versions', f'{id}.json')) as json_file:
        data = json.load(json_file)
        return render_template('version.html', versions=[data])

@app.route("/versions/<string:v1>/<string:v2>")
def get_version_diff(v1, v2):
    with open(os.path.join('versions', f'{v1}.json')) as json_file:
        data1 = json.load(json_file)

    with open(os.path.join('versions', f'{v2}.json')) as json_file:
        data2 = json.load(json_file)

    return render_template('version_diff.html', versions=[data1, data2])



@app.route('/render_versioning', methods=['GET', 'POST'])
def render_versioning():
    with open('combined.json') as json_file:
            data1 = json.load(json_file)
    versioning_data = data1 
    if request.method == 'POST':
        selected_version = request.form.get('version')
        if selected_version:
            for version in versioning_data["versions"]:
                if version["version"] == selected_version:
                    return render_template('versioning_template.html', versioning_data=versioning_data, selected_version=version)

    return render_template('versioning_template.html', versioning_data=versioning_data, selected_version=None)


if __name__ == '__main__':
    app.run(debug=True)