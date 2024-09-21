from flask import Flask, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///packages.db'
app.config['ADMIN_PASSWORD'] = 'mypass'  # Change to your desired password

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Package model
class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    duration = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    description = db.Column(db.String(255))  # Add this line if it's missing

# Route to display available packages
@app.route('/')
def home():
    packages = Package.query.all()
    return render_template('home.html', packages=packages)

# Route to handle package selection and payment
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    admin_password = app.config['ADMIN_PASSWORD'] 
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password != admin_password:
            return "Unauthorized", 403

        action = request.form.get('action')
        
        if action == 'add':
            package_name = request.form['name']
            package_price = request.form['price']
            package_duration = request.form['duration']
            package_image = request.form['image_url']
            package_description = request.form['description']
            new_package = Package()  # Create an instance of the Package class
            new_package.name = package_name
            new_package.price = float(package_price)
            new_package.duration = int(package_duration)
            new_package.image_url = package_image
            new_package.description = package_description
            db.session.add(new_package)
            db.session.commit()

        elif action == 'update':
            package_id = request.form['package_id']
            package = Package.query.get(package_id)
            if package is None:  # Check if package exists
                return "Package not found", 404  # Return an error if not found
            package.name = request.form['name']
            package.price = float(request.form['price'])
            package.duration = int(request.form['duration'])
            package.image_url = request.form['image_url']
            db.session.commit()

        elif action == 'delete':
            package_id = request.form['package_id']
            package = Package.query.get(package_id)
            db.session.delete(package)
            db.session.commit()

        return redirect(url_for('admin'))

    packages = Package.query.all()
    return render_template('admin.html', packages=packages)
@app.route('/purchase/<int:package_id>', methods=['GET', 'POST'])
def purchase(package_id):
    package = Package.query.get_or_404(package_id)
    if request.method == 'POST':
        # Integrate Safaricom Daraja payment
        return redirect(url_for('payment', package_id=package.id))
    return render_template('purchase.html', package=package)

if __name__ == '__main__':
    db.create_all()  
    app.run(host='0.0.0.0', port=5000)
