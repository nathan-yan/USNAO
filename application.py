from flask import Flask, jsonify, request, render_template , redirect, url_for
import bson
from pymongo import MongoClient

connection_string = "mongodb://admin:Mf5TB36utkjq1MLb@gradebook-cluster0-shard-00-00-l24me.mongodb.net:27017,gradebook-cluster0-shard-00-01-l24me.mongodb.net:27017,gradebook-cluster0-shard-00-02-l24me.mongodb.net:27017/test?ssl=true&replicaSet=GradeBook-Cluster0-shard-0&authSource=admin&retryWrites=true"

connection = MongoClient(connection_string)
db = connection['usnao']

registrations_location = db.registrations_location
registrations_student = db.registrations_student

app = Flask(__name__, static_url_path = "", static_folder = "static")
app.url_map.strict_slashes = False

photos = [] 
with open('photos.txt', 'r') as p:
    photos = p.readlines()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    else:
        print(request.form)
        form = request.form
        if (form['individual_school'] == "school"):
            print(registrations_location.insert_one({
                "first" : form['first'],
                "last" : form['last'],
                "email" : form['email'],
                "sname" : form['school_name'],
                "sloc" : form['school_address'],
                "description": form['description']
            }).inserted_id)
        elif (form['individual_school'] == 'individual'):
            print(registrations_student.insert_one({
                "first" : form['sfirst'],
                "last" : form['slast'],
                "email" : form['semail'],
                "teacher_email" : form['steacher-email'],
                "location" : bson.objectid.ObjectId(form['sschool_name_id']),
                "description": form['sdescription']
            }).inserted_id)
            
        
        return render_template('register_success.html')

@app.route("/locations", methods = ["GET"])
def locations():
    location_info = []
    cursor = registrations_location.find()

    for doc in cursor:
        location_info.append({
            "id" : str(doc['_id']),
            "address" : doc['sloc'],
            "name": doc['sname']
        })
    
    print(location_info)
    
    return jsonify({"locations" : location_info})

@app.route('/register-s')
def registers():
    return render_template('register_success.html')

@app.route("/about")
def about():
    return render_template('about.html')
    
@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/sli")
def sli():
    return render_template("sli.html")

@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/news")
def news():
    colors = ['#ffbcbc', '#ffc657', '#6e6bff', '#ba6dae', '#ea7272', '#6b94ff']
    list_articles = [[document['title'], 
                      colors[i % len(colors)],
                      document['link']] for i, document in enumerate(articles.find())]
    
    return render_template("news.html", titles = list_articles)

@app.route('/news/<article>')
def show_article(article):
    # Search for the article
    article = articles.find_one({
        "link" : '/news/' + article
    })

    if (article):
        return render_template('article.html', title = article['title'], markdown = article['markdown'])
    else:
        return 'hello',404

@app.route("/sponsorship")
def sponsorship():
    return render_template("sponsorship.html")

@app.route("/article")
def article():
    return render_template("article.html")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if (request.method == 'GET'):
        return render_template('login.html')
    else:
        password = request.form.get('password')
        if password == 'rocketry':
            return redirect(url_for("admin"))
        else:
            return redirect(url_for("login"))

@app.route('/admin')
def admin():
    return render_template('admin_control.html')

@app.route("/change-members")
def show_change_members():
    documents = members.find()

    return render_template("change_members.html", members = documents)

@app.route('/photos')
def show_members():

    # Oh my god please fix this soon
    
    return render_template('photos.html', photos = photos)

@app.route('/remove-member', methods = ['POST'])    # might want to merge this with change members later
def remove_member():
    name = request.form.get("name")
    print(name);
    member = members.delete_one({
        "name": name
    })

    print(member)

    if (member):
        return '', 200
    else:
        return '', 404

@app.route('/update-member-order', methods = ['POST'])    # might want to merge this with change members later
def update_member_order():

    return '', 200

@app.route('/create-article')
def create_article():
    return render_template('create_article.html')

@app.route("/publish-article", methods = ['POST'])
def publish_article():
    title = request.form.get('title')
    markdown = request.form.get('markdown')

    if (title == None or markdown == None):
        return "bad request"
    else:
        articles.insert_one({
            "title" : title,
            "markdown" : markdown,
            "link" : '/news/' + clean_title(title)
        })

        return jsonify({
            "status" : "success!"
        })

def clean_title(title):
    res = ''
    for a in title:
        if a.lower() in 'abcdefghijklmnopqrstuvwxyz0123456789-_':
            res += a.lower()
        elif a == ' ':
            res += '-'
    
    return res

app.run(debug = True)
