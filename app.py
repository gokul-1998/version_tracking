from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
import json
import json
import jsonpatch

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
    difference_json= db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<DashboardVersion %r>' % self.id
    
with app.app_context():
  db.create_all()


def apply_json_patch(original_json, json_patch):
    # Apply JSON Patch to the original JSON
    patched_json = jsonpatch.apply_patch(original_json, json_patch)
    return patched_json

def apply_patches(versions):
    # print(versions)
    resp=versions[0]
    for version in versions[1:]:
        resp=apply_json_patch(resp,version)
        # print(resp)
    return resp

def add_dashboard(name, description):
    dashboard = Dashboard(name=name, description=description)
    db.session.add(dashboard)
    db.session.commit()

def add_dashboard_version(dashboard_id, version, created_at, difference_json={}):
    dashboard_version = DashboardVersion(dashboard_id=dashboard_id, version=version, created_at=created_at, difference_json=difference_json)
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

def get_dashboard_version(id,dashboard_id=1):
    resp={}
    # to get the dashboard using the version passed in the url
    all_versions=DashboardVersion.query.filter_by(dashboard_id=dashboard_id).filter(DashboardVersion.version>=id).order_by(DashboardVersion.version.desc()).all()


    # all_versions=DashboardVersion.query.order_by(DashboardVersion.version.desc()).all()
    # print(all_versions)
    # print(id,all_versions[0].version)
    # print(id,all_versions[1].version)
    # print(type(id),type(all_versions[1].version))
    if id==all_versions[0].version:
        temp=all_versions[0].dashboard.get_dashboard()
        resp['dashboard']=temp
        resp['dashboard']['pages']=[page.get_page() for page in all_versions[0].dashboard.pages]
        for page in resp['dashboard']['pages']:
            page['widgets']=[widget.get_widget() for widget in Widget.query.filter_by(page_id=page['id']).all()]
        return resp
    if len(all_versions)==2:
        if id==all_versions[1].version:
            # print("in elif")
            return all_versions[1].difference_json
    elif len(all_versions)>2:
        # resp={}
        # temp=all_versions[1].difference_json
        # for version in all_versions[1:]:
        #     temp=apply_json_patch(temp,version.difference_json)
        # return temp
        lis=[version.difference_json for version in all_versions[1:]]
        return apply_patches(lis)
            
        
    


    # db_data= DashboardVersion.query.filter_by(id=id).first()
    
    # temp=db_data.dashboard.get_dashboard()
    # resp['dashboard']=temp
    # #  to get the pages less than the version passed in the url
    
    # resp['dashboard']['pages']=[page.get_page() for page in db_data.dashboard.pages]
    # for page in resp['dashboard']['pages']:
    #     page['widgets']=[widget.get_widget() for widget in Widget.query.filter_by(page_id=page['id']).all()]
    # return resp

with app.app_context():
    print(get_dashboard_version(1))
import json
import jsonpatch



@app.route('/')
def index():
    # the url will be /?dashboard_id=1&version=1
    # db_version=DashboardVersion.query.filter_by(id=1).first()
    dashboard_id=request.args.get('dashboard_id',1)
    version=request.args.get('version','latest')
    if version=="latest":
        db_version=DashboardVersion.query.filter_by(dashboard_id=dashboard_id).order_by(DashboardVersion.version.desc()).first()
        version=db_version.version
    else:   
        db_version=DashboardVersion.query.filter_by(dashboard_id=dashboard_id,version=int(version)).first()
    print("db_version",version)
    print("db_version",type(version))
    dashboard_data=get_dashboard_version(int(version))
    print("dashboard_data",dashboard_data)
    # to order by descending order of  version till the version passed in the url
    sub_versions_including_current=DashboardVersion.query.filter_by(dashboard_id=dashboard_id).filter(DashboardVersion.version>=version).order_by(DashboardVersion.version.desc()).all()

    all_versions=DashboardVersion.query.filter_by(dashboard_id=dashboard_id).order_by(DashboardVersion.version.desc()).all()
    all_versions_json=[version.difference_json for version in sub_versions_including_current]

    # final=apply_patches(all_versions_json)
    # print("final",final)
    # if not final:

    #     final=dashboard_data
    # else:

    #     final=(final)
    #     final['dashboard']=dashboard_data['dashboard']
    #     final['dashboard']['pages']=dashboard_data['dashboard']['pages']
    #     for page in final['dashboard']['pages']:
    #         page['widgets']=[widget for widget in page['widgets'] if widget['id'] in final['dashboard']['pages'][0]['widgets']]
    return render_template('index.html',dashboard_data=dashboard_data,current_version=version,all_versions=all_versions)

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
# @app.route("/versions")
# def get_all_versions():
#     version_files = os.listdir('versions')
#     versions = []

#     for filename in version_files:
#         with open(os.path.join('versions', filename)) as json_file:
#             data = json.load(json_file)
#             versions.append(data)

#     return render_template('version.html', versions=versions)

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

import json
import jsonpatch

def generate_json_patch(new_json, old_json):
    # Generate JSON Patch
    patch = jsonpatch.make_patch(new_json, old_json)
    return json.loads(patch.to_string())
def apply_json_patch(original_json, json_patch):
    # Apply JSON Patch to the original JSON
    patched_json = jsonpatch.apply_patch(original_json, json_patch)
    return patched_json


@app.route("/bla")
def bla():
    version=1
    difference_json=json.loads(json.dumps(get_dashboard_version(1)))
    print(difference_json)
    print(type(difference_json))
    # to jsonify the json
    difference_json=json.dumps(difference_json)
    print(type(difference_json))
    # to add to the database as json
    difference_json=json.loads(difference_json)
    return difference_json
           

@app.route('/add_version/<int:dashboard_id>', methods=['GET', 'POST'])
def add_version(dashboard_id):
    # create a json file for the version
    db_version=DashboardVersion.query.filter_by(dashboard_id=dashboard_id).order_by(DashboardVersion.version.desc()).all()[:2]
    print("last two db_version",db_version)

    if len(db_version)<=1:

        for version in db_version:
            print(f"get_dashboard_version {version.version}",get_dashboard_version(int(version.version)))
            version.difference_json=json.loads(json.dumps(get_dashboard_version(int(version.version))))
            print(version.difference_json)
            print(type(version.difference_json))
            
            db.session.commit()
            # return version.difference_json

        
    else:
        print("inside else")
        print(f"get version difference {db_version[0].version}",get_dashboard_version(db_version[0].version))
        print(f"get version difference {db_version[1].version}",get_dashboard_version(db_version[1].version))
        db_version[0].difference_json=get_dashboard_version(db_version[0].version)
        db_version[1].difference_json=generate_json_patch(get_dashboard_version(db_version[0].version),get_dashboard_version(db_version[1].version))
        db.session.commit()
    # db_version.difference_json=json.dumps(db_version[0].difference_json)
    version=db_version[0].version+1
    add_dashboard_version(dashboard_id, version, datetime.now(),get_dashboard_version(version-1))
    # db.session.commit()
    return redirect(url_for('index'))
    # get the dashboard data
    # get the page data
    # get the widget data
    # write to json file
    # add the version to the dashboard version table

    # with open(f'versions/{filename}.json', 'w') as outfile:
    #     json.dump(resp, outfile)

    
    # return redirect(url_for('index'))

@app.route("/delete_version/<int:dashboard_id>/<int:version>")
def delete_version(dashboard_id,version):
    db_version=DashboardVersion.query.filter_by(dashboard_id=dashboard_id,version=version).first()
    db.session.delete(db_version)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)