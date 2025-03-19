from flask import Flask, render_template, request,redirect,url_for,flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from models import db, User, Professional, Services, Service_Request
from sqlalchemy.exc import IntegrityError
import matplotlib.pyplot as plt
import os


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///astha.sqlite"
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)
print("Household Solutions is started...")
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user_login' , methods = ["GET","POST"])
def signin_user():
    if request.method == "POST":
        email = request.form.get("email")
        pwd = request.form.get("password")
        usr = User.query.filter_by(email = email, password = pwd).first()
        if usr:
            session['user_id'] = usr.id
            if usr.is_block == True:
                flash("Your account has been blocked by the admin,contact them")
                return redirect(url_for('signin_user'))
            return redirect(url_for("customer_dashboard"))
    return render_template("user_login.html")

@app.route("/user_register", methods=["GET", "POST"])
def signup_user():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        pwd = request.form.get("password")
        address = request.form.get("address")
        contact = request.form.get("contact")
        
        # Check if the user already exists
        usr = User.query.filter_by(email=email).first()
        if usr:
            flash("Email already exists! Please login instead.", "error")
            return redirect(url_for("signin_user"))

        # If the user does not exist, create a new one
        new_user = User(name=name, email=email, password=pwd, address=address, contact=contact)
        db.session.add(new_user)
        db.session.commit()
        
        # Redirect to the login page after successful signup
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("signin_user"))
    return render_template("user_signup.html")  # Render signup page if GET request

@app.route("/professional_signup", methods=["GET", "POST"])
def signup_professional():
    services = Services.query.all()
    if request.method == "POST":
        name = request.form.get("name")
        contact = request.form.get("contact")
        address = request.form.get("address")
        exp = request.form.get("experience")
        profession_id = request.form.get("profession")
        email = request.form.get("email")
        pwd = request.form.get("password")
        
        # Check if the professional already exists
        usr = Professional.query.filter_by(email=email).first()
        if usr:
            flash("Email already exists! Please login instead.", "error")
            return redirect(url_for("signin_professional"))

        # If the professional does not exist, create a new one
        new_professional = Professional(name=name, contact=contact,  address=address, experience=exp, email=email, password=pwd,profession_id=profession_id)
        db.session.add(new_professional)
        db.session.commit()
        
        # Redirect to the professional login page after successful signup
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("signin_professional"))

    return render_template("professional_signup.html",services=services)  # Render signup page if GET request

@app.route("/professional_login" , methods = ["GET","POST"])
def signin_professional():
    if request.method == "POST":
        email = request.form.get("email")
        pwd = request.form.get("password")
        usr = Professional.query.filter_by(email = email, password = pwd).first()
        if usr:
            session['user_id'] = usr.id
            if usr.is_approved == False:
                flash("your account has not been approved bythe admin,please wait or try contacting them")
                return redirect(url_for('signin_professional'))
            if usr.is_block == True:
                flash("Your account has been blocked by the admin,contact them")
                return render_template("professional_login.html")
            return redirect(url_for('professional_dashboard'))
    return render_template("professional_login.html")

#------------------------------------------------------------- ADMIN FUNCTIONALITIES --------------------------------------------------
ADMIN_USERNAME = "Astha_Sahu"
ADMIN_PASSWORD = "astha0204"
@app.route('/admin_login' , methods = ["GET","POST"])
def signin_admin():
    if request.method == "POST":
        admin_username = request.form.get("username")
        pwd = request.form.get("password")
        if admin_username == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['username'] = admin_username
            return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.route('/admin_dashboard', methods=['POST','GET'])
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('signin_admin'))
    pending_professionals = Professional.query.filter(Professional.is_approved == False).all()
    approved_professionals = Professional.query.filter(Professional.is_approved == True).all()
    services = Services.query.all()
    users = User.query.all()
    
    professional_name_query=request.args.get('name','').strip()
    professional_id_query=request.args.get('professional_id','').strip()

    query=Professional.query
    if professional_name_query:
        query=query.filter(Professional.name.ilike(f'%{professional_name_query}%'))
    if professional_id_query:
        if professional_id_query.isdigit():
            query = query.filter(Professional.id == int(professional_id_query))
        else:
            return "Invalid search for service id",400
    result = query.all()
    return render_template("admin_dashboard.html",users = users, pending_professionals = pending_professionals, approved_professionals = approved_professionals, services = services, result=result)

@app.route('/approve_professional',methods = ['POST'])
def approve_professional():
    professional_id = request.form.get('id')
    professional = Professional.query.get(professional_id)
    if not professional:
        flash("No professionals found", "error")
        return redirect(url_for("admin_dashboard"))
    professional.is_approved = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/decline_professional',methods = ['POST'])
def decline_professional():
    professional_id = request.form.get('id')
    professional = Professional.query.get(professional_id)
    if not professional:
        flash("No professionals found", "error")
        return redirect(url_for("admin_dashboard"))
    professional.is_approved = False
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route('/delete_service/<int:service_id>',methods = ['POST'])
def delete_service(service_id):
    service = Services.query.get(service_id)
    if service:
        db.session.delete(service)
        db.session.commit()
    return redirect(url_for("admin_dashboard"))
    
@app.route('/edit_service/<int:service_id>', methods=['POST', 'GET'])
def edit_service(service_id):
    # Fetch the service by service_id
    service = Services.query.filter_by(service_id=service_id).first()
    if not service:
        flash("Service not found!", "error")
        return redirect(url_for("admin_dashboard"))  # Redirect to admin dashboard if service doesn't exist

    if request.method == 'POST':
        # Get the new name from the form
        new_name = request.form.get("new_name")
        new_date_created = request.form.get("new_date_created")
        new_description = request.form.get("new_description")
        new_time_required = request.form.get("new_time_required")
        new_base_price = request.form.get("new_base_price")

        # Check if the new name is empty
        if not new_name:
            flash("Service name cannot be empty.", "error")
            return redirect(url_for("edit_service", service_id=service_id))

        # Ensure the new name is unique
        duplicate_service = Services.query.filter(Services.name == new_name, Services.service_id != service_id).first()
        if duplicate_service:
            flash("Service with this name already exists!", "error")
            return redirect(url_for("edit_service", service_id=service_id))

        try:
            # Update the service name
            service.name = new_name
            service.date_created = new_date_created
            service.description = new_description
            service.time_required = new_time_required
            service.base_price = new_base_price

            db.session.commit()
            flash("Service updated successfully!", "success")
            return redirect(url_for("admin_dashboard"))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating service: {e}")
            flash("An error occurred while updating the service. Please try again.", "error")
            return redirect(url_for("edit_service", service_id=service_id))

    # Render the edit service page with the current service name
    return render_template("edit_service.html", service_id=service.service_id, current_name=service.name)

@app.route('/create_service', methods=['POST', 'GET'])
def create_service():
    if request.method == 'POST':
        name = request.form.get("name")
        date_created = request.form.get("date_created")
        description = request.form.get("description")
        time_required = request.form.get("time_required")
        base_price = request.form.get("base_price")

        # Validate that name is not empty
        if not name or not name.strip():
            flash("Service name cannot be empty.", "error")
            return redirect(url_for('create_service'))

        # Check for duplicate service
        service = Services.query.filter_by(name=name.strip()).first()
        if service:
            flash("Service already exists!", "error")
            return redirect(url_for('create_service'))

        try:
            # Create a new service
            new_service = Services(name=name.strip(),date_created=date_created,description=description,time_required=time_required,base_price=base_price)
            db.session.add(new_service)
            db.session.commit()
            flash("Service created successfully!", "success")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating service: {e}")
            flash("An error occurred while creating the service. Please try again.", "error")
            return redirect(url_for('create_service'))
        return redirect(url_for('admin_dashboard'))

    return render_template("create_new_service.html")
    
@app.route('/block_professional',methods = ['POST'])
def block_professional():
    professional_id = request.form.get('id')
    professional = Professional.query.get(professional_id)
    if not professional:
        flash("No professionals found", "error")
        return redirect(url_for("admin_dashboard"))
    professional.is_block = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/unblock_professional',methods = ['POST'])
def unblock_professional():
    professional_id = request.form.get('id')
    professional = Professional.query.get(professional_id)
    if not professional:
        flash("No professionals found", "error")
        return redirect(url_for("admin_dashboard"))
    professional.is_block = False
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route('/block_user',methods = ['POST'])
def block_user():
    user_id = request.form.get('id')
    user = User.query.get(user_id)
    if not user:
        flash("No users found", "error")
        return redirect(url_for("admin_dashboard"))
    user.is_block = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/unblock_user',methods = ['POST'])
def unblock_user():
    user_id = request.form.get('id')
    user = User.query.get(user_id)
    if not user:
        flash("No users found", "error")
        return redirect(url_for("admin_dashboard"))
    user.is_block = False
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route('/summary',methods=['POST','GET'])
def summary():
    customer_data  = db.session.query(User.name,db.func.count(Service_Request.id)).join(Service_Request).group_by(User.id).all()
    names = [user[0] for user in customer_data]
    request_count = [user[1] for user in customer_data]

    plt.figure(figsize=(10,6))
    plt.bar(names,request_count,color='skyblue')
    plt.xlabel('Customer')
    plt.ylabel('Number of request')
    plt.title('Number  of request per Customer')
    plt.xticks(rotation=45,ha='right')
    plt.tight_layout()

    graph_path = os.path.join('static','customer_request_grapth.png')
    plt.savefig(graph_path)
    plt.close()
    return render_template('summary.html',graph_url=url_for('static',filename='customer_request_grapth.png'))

#---------------------------------------CUSTOMER DASHBOARD----------------------------------------------

@app.route('/customer_dashboard',methods = ['POST','GET'])
def customer_dashboard():
    if 'user_id' not in session:
        flash("user not logged in")
        return redirect(url_for('signin_user'))
    services = Services.query.all()
    service_requests = Service_Request.query.filter_by(customer_id=session['user_id'])

    name_query=request.args.get('name','').strip()
    service_id_query=request.args.get('service_id','').strip()

    query=Services.query
    if name_query:
        query=query.filter(Services.name.ilike(f'%{name_query}%'))
    if service_id_query:
        if service_id_query.isdigit():
            query = query.filter(Services.service_id == int(service_id_query))
        else:
            return "Invalid search for service id",400
    result = query.all()
    return render_template("user_dashboard.html",services = services, service_requests=service_requests, result=result)

@app.route('/create_service_request/',methods = ['POST','GET'])
def create_service_request():
    if 'user_id' not in session:
        flash("user not logged in")
        return redirect(url_for('signin_user'))
    customer_id = session['user_id']
    customer = User.query.filter_by(id=customer_id).first()
    if not customer:
        flash("customer not found", "error")
        return redirect(url_for('signin_user'))
    services = Services.query.all()
    if request.method == 'POST':
        service_id = request.form.get("service")
        date_of_service = request.form.get("date_of_service")
        description = request.form.get("description")
        offered_Price = request.form.get("offered_price")
        customer_id = customer_id

        new_request = Service_Request(customer_id=customer_id, request_for_service_id=service_id, date_of_service=date_of_service, description=description, offered_Price=offered_Price)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for("customer_dashboard"))
    return render_template("new_request.html",services=services)

@app.route('/edit_service_request/<int:request_id>',methods = ['POST','GET'])
def edit_service_request(request_id):
    if 'user_id' not in session:
        flash("user not logged in")
        return redirect(url_for('signin_user'))
    services = Services.query.all()
    service_request = Service_Request.query.filter_by(id=request_id).first()
    if not service_request:
        flash("Request not found","error")
        return redirect(url_for("customer_dashboard"))

    if request.method == 'POST':
        new_service_id = request.form.get("service")
        new_date_of_service = request.form.get("date_of_service")
        new_description = request.form.get("description")
        new_offered_price = request.form.get("offered_price")
        
        service_request.request_for_service_id = new_service_id
        service_request.date_of_service = new_date_of_service
        service_request.description = new_description
        service_request.offered_price = new_offered_price

        db.session.commit()
        return redirect(url_for("customer_dashboard"))
    return render_template("edit_request.html",services=services,request_id=service_request.id)

@app.route('/close_request_user',methods = ['POST','GET'])
def close_request_user():
    if 'user_id' not in session:
        flash("please login ")
        return redirect(url_for('signin_professional'))
    
    service_request_id = int(request.form.get('id'))
    service_request = Service_Request.query.filter_by(id=service_request_id).first()
    if not service_request:
        flash("No service request found")
        return redirect(url_for('customer_dashboard'))
    service_request.status = 'closed'
    db.session.commit()
    return redirect(url_for('customer_dashboard'))

#----------------------------PROFESSIONAL DASHBOARD--------------------

@app.route('/professional_dashboard',methods=['POST','GET'])
def professional_dashboard():
    if 'user_id' not in session:
        flash("please login ")
        return redirect(url_for('signin_professional'))
    professional = Professional.query.filter_by(id=session['user_id']).first()
    if not professional:
        flash("professional not logged in")
        return redirect(url_for('signin_professional'))
    service_requests = Service_Request.query.filter_by(request_for_service_id=professional.profession_id,assigned=False).all()
    accepted_service_requests = Service_Request.query.filter_by(request_for_service_id=professional.profession_id,assigned=True,professional_id=professional.id).all()
    return render_template('professional_dashboard.html', service_requests=service_requests,accepted_service_requests=accepted_service_requests)

@app.route('/accept',methods=['POST'])
def accept():
    if 'user_id' not in session:
        flash("please login ")
        return redirect(url_for('signin_professional'))
    professional_id = session['user_id']

    service_request_id = int(request.form.get('id'))
    service_request = Service_Request.query.filter_by(id=service_request_id).first()
    if not service_request:
        flash("No service request found")
        return redirect(url_for('professional_dashboard'))
    service_request.assigned = True
    service_request.professional_id = professional_id
    service_request.status = 'accepted'
    db.session.commit()
    return redirect(url_for('professional_dashboard'))

@app.route('/reject',methods=['POST'])
def reject():
    if 'user_id' not in session:
        flash("please login ")
        return redirect(url_for('signin_professional'))
    service_request_id = int(request.form.get('id'))
    service_request = Service_Request.query.filter_by(id=service_request_id).first()
    if not service_request:
        flash("No service request found")
        return redirect(url_for('professional_dashboard'))
    service_request.assigned = False
    service_request.professional_id = None
    service_request.status = 'rejected'
    db.session.commit()
    return redirect(url_for('professional_dashboard'))

@app.route('/close_request',methods = ['POST','GET'])
def close_request():
    if 'user_id' not in session:
        flash("please login ")
        return redirect(url_for('signin_professional'))
    
    service_request_id = int(request.form.get('id'))
    service_request = Service_Request.query.filter_by(id=service_request_id).first()
    if not service_request:
        flash("No service request found")
        return redirect(url_for('professional_dashboard'))
    service_request.status = 'completed'
    db.session.commit()
    return redirect(url_for('professional_dashboard'))

@app.route('/logout',methods=['POST','GET'])
def logout():
    session.pop('user_id',None)
    return redirect(url_for('home')) 

@app.route('/logout_admin',methods=['POST','GET'])
def logout_admin():
    session.pop('username',None)
    return redirect(url_for('home'))

with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug = True)
