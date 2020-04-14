from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)

# base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init the Database
db = SQLAlchemy(app)

# Init Marshmallow
marsh = Marshmallow(app)

################################################################### INVESTOR CLASS/ENTITY #####################################################################################
class Investor(db.Model):
    investorId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    dateOfBirth = db.Column(db.String(40))

    def __init__(self, name, dob):
        self.name = name
        self.dateOfBirth = dob

# Investor Schema
class InvestorSchema(marsh.Schema):
    class Meta:
        fields = ('investorId', 'name', 'dateOfBirth')

# Init the schema
investor_schema = InvestorSchema()    # dealing with a single investor
investors_schema = InvestorSchema(many=True)  # dealing with many investors

# Create an investor
@app.route('/investor', methods=['POST'])
def addInvestor():
    name = request.json['name']
    dateOfBirth = request.json['dateOfBirth']

    newInvestor = Investor(name, dateOfBirth)

    db.session.add(newInvestor)
    db.session.commit()

    return investor_schema.jsonify(newInvestor)

# Get single Investor
@app.route('/investor/<investorId>', methods=['GET'])
def getInvestor(investorId):
    investor = Investor.query.get(investorId)
    return investor_schema.jsonify(investor)

# Get All Investors
@app.route('/investor', methods=['GET'])
def getAllInvestors():
    allInvestors = Investor.query.all()
    result = investors_schema.dump(allInvestors)
    return jsonify(result)

# Update an Investor
@app.route('/investor/<investorId>', methods=['PUT'])
def updateInvestor(investorId):
    investor = Investor.query.get(investorId)

    name = request.json['name']
    dateOfBirth = request.json['dateOfBirth']

    investor.name = name
    investor.dateOfBirth = dateOfBirth

    db.session.commit()

    return investor_schema.jsonify(investor)

# Delete Investor
@app.route('/investor/<investorId>', methods=['DELETE'])
def deleteInvestor(investorId):
    investor = Investor.query.get(investorId)
    db.session.delete(investor)
    db.session.commit()
    return investor_schema.jsonify(investor)

############################################################# REPORT CLASS/ENTITY ####################################################################################################
class Company(db.Model):
    companyName = db.Column(db.String(50), primary_key=True)
    industry = db.Column(db.String(30))
    sharesOutstanding = db.Column(db.Integer)
    marketCap = db.Column(db.Integer)

    def __init__(self, name, industry, sot, mc):
        self.companyName = name
        self.industry = industry
        self.sharesOutstanding = sot
        self.marketCap = mc

# Company Schema
class CompanySchema(marsh.Schema):
        class Meta:
            fields = ('companyName', 'industry', 'sharesOustanding', 'marketCap')

# Init the Schema
company_schema = CompanySchema()
companies_schema = CompanySchema(many=True)

# Add a Company to the database
@app.route('/company', methods=['POST'])
def addCompany():
    companyName = request.json['companyName']
    industry = request.json['industry']
    sharesOustanding = request.json['sharesOutstanding']
    marketCap = request.json['marketCap']

    newCompany = Company(companyName, industry, sharesOustanding, marketCap)

    db.session.add(newCompany)
    db.session.commit()
    return company_schema.jsonify(newCompany)

# Get a single Company
@app.route('/company/<companyName>', methods=['GET'])
def getCompany(companyName):
    company = Company.query.get(companyName)
    return company_schema.jsonify(company)

# Update a company
@app.route('/company/<companyName>', methods=['PUT'])
def updateCompany(companyName):
    company = Company.query.get(companyName)

    companyName = request.json['companyName']
    industry = request.json['industry']
    sharesOustanding = request.json['sharesOutstanding']
    marketCap = request.json['marketCap']

    company.companyName = companyName
    company.industry = industry
    company.sharesOustanding = sharesOustanding
    company.marketCap = marketCap

    db.session.commit()
    return company_schema.jsonify(company)

# Delete company from the database
@app.route('/company/<companyName>', methods=['DELETE'])
def deleteCompany(companyName):
    company = Company.query.get(companyName)
    db.session.delete(company)
    db.session.commit()
    return company_schema.jsonify(company)

# Run server
if __name__ == '__main__':
    app.run(debug=True)
