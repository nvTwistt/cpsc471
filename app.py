from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow

import os

import random



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
    investment = db.relationship('Investment', backref='investor', lazy=True)


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
    indicateToInvest = db.relationship('Investment_Option', backref='company', lazy=True)

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



############################################################# Portfolio Class ####################################################################################################

class Portfolio(db.Model):

    portfolioId = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.Float, nullable=True)

    accountId = db.Column(db.Integer) #db.ForeignKey('account.accountId'))
    bonds = db.relationship('Portfolio_Bond', backref='portfolio', lazy=True)
    canadianEquities = db.relationship('Portfolio_Canadian_Equity', backref='portfolio', lazy=True)
    usEquities = db.relationship('Portfolio_US_Equity', backref='portfolio', lazy=True)

    def __init__(self, accountId):
        self.accountId = accountId



# Portfolio Schema
class PortfolioSchema(marsh.Schema):
        class Meta:
            fields = ('portfolioId', 'value', 'accountId')



# Init the Schema
portfolio_schema = PortfolioSchema()
portfolios_schema = PortfolioSchema(many=True)


# Create a portfolio

@app.route('/portfolio', methods=['POST'])
def addPortfolio():
    accountId = request.json['accountId']
    bonds = request.json['bonds']
    canadianEquities = request.json['canadianEquities']
    usEquities = request.json['usEquities']


    newPortfolio = Portfolio(accountId)
    db.session.add(newPortfolio)
    db.session.commit()

    totalValue = 0.0

    for x in bonds:
      newBond = Portfolio_Bond(newPortfolio.portfolioId, x)
      db.session.add(newBond)
      totalValue+=x


    for x in canadianEquities:
      newEquity = Portfolio_Canadian_Equity(newPortfolio.portfolioId, x)
      db.session.add(newEquity)
      totalValue+=x

    for x in usEquities:
      newEquity = Portfolio_US_Equity(newPortfolio.portfolioId, x)
      db.session.add(newEquity)
      totalValue+=x

    newPortfolio.value = totalValue

    db.session.commit()

    return portfolio_schema.jsonify(newPortfolio)

@app.route('/portfolio/id:<portfolioId>', methods=['GET'])
def getPortfolio(portfolioId):
    portfolio = Portfolio.query.get(portfolioId)
    return portfolio_schema.jsonify(portfolio)

@app.route('/portfolio/<accountId>', methods=['GET'])
def getAccountPortfolios(accountId):
    portfolios = Portfolio.query.filter_by(accountId = accountId).all()
    return portfolios_schema.jsonify(portfolios)

@app.route('/portfolio/<portfolioId>', methods = ['DELETE'])
def deletePortfolio(portfolioId):
  portfolio = Portfolio.query.get(portfolioId)
  db.session.delete(portfolio)
  db.session.commit()
  return portfolio_schema.jsonify(portfolio)  

############################################################# Portfolio Bond Class ####################################################################################################

class Portfolio_Bond(db.Model):

    portfolioId = db.Column(db.Integer, db.ForeignKey('portfolio.portfolioId'))
    bondId = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)

    def __init__(self, portfolioId, amount):
        self.portfolioId = portfolioId
        self.amount = amount

# Portfolio Schema
class Portfolio_BondSchema(marsh.Schema):
        class Meta:
            fields = ('portfolioId', 'bondId', 'amount')



# Init the Schema
portfolio_bond_schema = Portfolio_BondSchema()
portfolios_bond_schema = Portfolio_BondSchema(many=True)

############################################################# Portfolio Canadian Equity Class ####################################################################################################

class Portfolio_Canadian_Equity(db.Model):

    portfolioId = db.Column(db.Integer, db.ForeignKey('portfolio.portfolioId'))
    canadianEquityId = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)

    def __init__(self, portfolioId, amount):
        self.portfolioId = portfolioId
        self.amount = amount


# Portfolio Schema
class Portfolio_Canadian_EquitySchema(marsh.Schema):
        class Meta:
            fields = ('portfolioId', 'canadianEquityId', 'amount')


# Init the Schema
portfolio_Canadian_Equity_schema = Portfolio_Canadian_EquitySchema()
portfolios_Canadian_Equity_schema = Portfolio_Canadian_EquitySchema(many=True)

############################################################# Portfolio US Equity Class ####################################################################################################
class Portfolio_US_Equity(db.Model):

    portfolioId = db.Column(db.Integer, db.ForeignKey('portfolio.portfolioId'))
    usEquityId = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)

    def __init__(self, portfolioId, amount):
        self.portfolioId = portfolioId
        self.amount = amount

# Portfolio Schema
class Portfolio_US_EquitySchema(marsh.Schema):
        class Meta:
            fields = ('portfolioId', 'usEquityId', 'amount')



# Init the Schema
portfolio_US_Equity_schema = Portfolio_US_EquitySchema()
portfolios_US_Equity_schema = Portfolio_US_EquitySchema(many=True)


############################################################# Investment Class ####################################################################################################

class Investment(db.Model):

    referenceId = db.Column(db.Integer, primary_key=True)
    investorId = db.Column(db.Integer, db.ForeignKey('investor.investorId'))

    holding = db.Column(db.String(50))
    marketValue = db.Column(db.Float)

    def __init__(self, referenceId, investorId, holding, marketValue):
        self.referenceId = referenceId
        self.investorId = investorId
        self.holding = holding
        self.marketValue = marketValue


# Portfolio Schema
class InvestmentSchema(marsh.Schema):
        class Meta:
            fields = ('referenceId', 'investorId', 'holding', 'marketValue')


# Init the Schema
investment_schema = InvestmentSchema()
investments_schema = InvestmentSchema(many=True)

@app.route('/investment/<referenceId>', methods=['GET'])
def getInvestment(referenceId):
    investment = Investment.query.get(referenceId)
    return investment_schema.jsonify(investment)

class Investment_Option(db.Model):

    referenceId = db.Column(db.Integer, primary_key=True)
    advisorId = db.Column(db.Integer, db.ForeignKey('advisor.advisorID'))
    amount = db.Column(db.Integer)
    invType = db.Column(db.String(10))
    companyName = db.Column(db.String(50), db.ForeignKey('company.companyName'))

    def __init__(self, advisorId, amount, invType, company):
        self.advisorId = advisorId
        self.amount = amount
        self.invType = invType
        self.companyName = company

# Portfolio Schema
class Investment_OptionSchema(marsh.Schema):
        class Meta:
            fields = ('referenceId', 'advisorId', 'amount', 'company', 'invType')


# Init the Schema
investment_option_schema = Investment_OptionSchema()
investment_options_schema = Investment_OptionSchema(many=True)

@app.route('/investment', methods=['POST'])
def addInvestment():
  advisorId = request.json['advisorId']
  amount = request.json['amount']
  company = request.json['company']
  invType = request.json['invType']
  
  newInvestmentOption = Investment_Option(advisorId, amount, invType, company)
  db.session.add(newInvestmentOption)
  db.session.commit()
  return investment_option_schema.jsonify(newInvestmentOption)

@app.route('/investment/options/<advisorId>', methods=['GET'])
def getInvestmentOptions(advisorId):
    options = Investment_Option.query.filter_by(advisorId = advisorId).all()
    return investment_options_schema.jsonify(options)

####################################################### ADVISOR CLASS ##############################################################################################
class Advisor(db.Model):

    advisorID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(200))
    qualifications = db.relationship('Advisor_Qualification', backref='advisor', lazy=True)
    investmentOptions = db.relationship('Investment_Option', backref='advisor', lazy=True)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password

# Advisor Schema
class AdvisorSchema(marsh.Schema):
        class Meta:
            fields = ('advisorID', 'name', 'username', 'password')

# Init the Schema

advisor_schema = AdvisorSchema()
advisors_schema = AdvisorSchema(many=True)

# Add an advisor into the data base

@app.route('/advisor', methods=['POST'])
def addAdvisor():
  name = request.json['name']
  username = request.json['username']
  password = request.json['password']
  qualifications = request.json['qualifications']
  
  newAdvisor = Advisor(name, username, password)
  db.session.add(newAdvisor)
  db.session.commit()

  for x in qualifications:
      newQualification = Advisor_Qualification(newAdvisor.advisorID, x)
      db.session.add(newQualification)

  db.session.commit()

  return advisor_schema.jsonify(newAdvisor)

#get a single advisor via advisorID
#GET /advisor/{AdvisorID}

@app.route('/advisor/<advisorID>', methods = ['GET'])
def getAdvisor(advisorID):
  advisor = Advisor.query.get(advisorID)
  return advisor_schema.jsonify(advisor)

#get all advisors
@app.route('/advisor', methods = ['GET'])
def getAllAdvisors():
  allAdvisors = Advisor.query.all()
  result = advisors_schema.dump(allAdvisors)
  return jsonify(result)

# GET/advisor/{advisorID}/investors
#retrueve the list of investors an advisor is advertising
@app.route('/advisors/<advisorID>/investors', methods = ['GET'])
def getAdvisedInvestors(advisorID):
  #advisor = Advisor.query.get(advisorID)
  AdvisedInvestors = Investor.query.filter_by(advisorID = (Advisor.query.get(advisorID))).all()
  result = investors_schema.dump(AdvisedInvestors)
  return jsonify(result)

#update advisors 
# @app.route('/advisor/<advisorID>', methods = ['PUT'])
# def updateAdvisor(advisorID):
#   advisor = Advisor.query.get(advisorID)
#   name = request.json['name']
#   username = request.json['username']
#   password = request.json['password']
#   qualifications = request.json['qualifications']

#   advisor.name = name
#   advisor.username = username
#   advisor.password = password
#   advisor.qualifications = qualifications

#   db.session.commit()

#   return advisor_schema.jsonify(advisor)


#delete advisor
@app.route('/advisor/<advisorID>', methods = ['DELETE'])
def deleteAdvisor(advisorID):
  advisor = Advisor.query.get(advisorID)
  db.session.delete(advisor)
  db.session.commit()
  return advisor_schema.jsonify(advisor)    

####################################################### ADVISOR Qualification CLASS ##############################################################################################
class Advisor_Qualification(db.Model):
    advisorId = db.Column(db.Integer, db.ForeignKey('advisor.advisorID'), primary_key=True)
    qualification = db.Column(db.String(50), primary_key=True)

    def __init__(self, advisorId, qual):
        self.advisorId = advisorId
        self.qualification = qual

# Advisor Qualification Schema
class Advisor_QualificationSchema(marsh.Schema):
        class Meta:
            fields = ('advisorId', 'qualification')

Advisor_Qualification_schema = Advisor_QualificationSchema()
Advisor_Qualifications_schema = Advisor_QualificationSchema(many=True)

  



# Run server

if __name__ == '__main__':

    app.run(debug=True)