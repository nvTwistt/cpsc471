from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import func
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
    advisorId = db.Column(db.Integer, db.ForeignKey('advisor.advisorId'))
    accountId = db.Column(db.Integer, db.ForeignKey('account.accountId'))
    investment = db.relationship('Investment', backref='investor', lazy=True)
    portfolio = db.relationship('Portfolio', backref='investor', lazy=True)
    survey = db.relationship('Survey', backref='investor', lazy=True)

    def __init__(self, name, dob, advisorId, accountId):
        self.name = name
        self.dateOfBirth = dob
        self.advisorId = advisorId
        self.accountId = accountId

# Investor Schema
class InvestorSchema(marsh.Schema):
    class Meta:
        fields = ('investorId', 'name', 'dateOfBirth', 'advisorId', 'accountId')


# Init the schema
investor_schema = InvestorSchema()    # dealing with a single investor
investors_schema = InvestorSchema(many=True)  # dealing with many investors


# Create an investor
@app.route('/investor', methods=['POST'])
def addInvestor():
    name = request.json['name']
    dateOfBirth = request.json['dateOfBirth']
    username = request.json['username']
    password = request.json['password']

    newAccount = Account(username, password, False)
    db.session.add(newAccount)
    db.session.commit()

    newInvestor = Investor(name, dateOfBirth, leastBusyAdvisor().advisorId, newAccount.accountId)

    db.session.add(newInvestor)
    db.session.commit()

    return investor_schema.jsonify(newInvestor)

#Stored procedure that finds the advisor with the least investors assigned to them
def leastBusyAdvisor():
    advisorId = Advisor.query.\
            with_entities(Advisor.advisorId).\
            outerjoin(Investor).\
            group_by(Advisor.advisorId).\
            order_by(func.count(Investor.investorId)).first()
    return advisorId


# Get single Investor
@app.route('/investor/<investorId>', methods=['GET'])
def getInvestor(investorId):
    investor = Investor.query.get(investorId)
    return investor_schema.jsonify(investor)

# Update an Investor
@app.route('/investor/<investorId>', methods=['PUT'])
def updateInvestor(investorId):
    investor = Investor.query.get(investorId)

    name = request.json['name']
    dateOfBirth = request.json['dateOfBirth']
    password = request.json['password']

    account = Account.query.get(investor.accountId)

    investor.name = name
    investor.dateOfBirth = dateOfBirth
    account.password = password

    db.session.commit()

    return investor_schema.jsonify(investor)

# Delete Investor
@app.route('/investor/<investorId>', methods=['DELETE'])
def deleteInvestor(investorId):
    investor = Investor.query.get(investorId)

    db.session.delete(investor)
    db.session.commit()

    return investor_schema.jsonify(investor)

############################################################# Survey CLASS ####################################################################################################
class Survey(db.Model):
    investorId = db.Column(db.Integer, db.ForeignKey('investor.investorId'), primary_key=True)
    advisorId = db.Column(db.Integer, db.ForeignKey('advisor.advisorId'))
    riskTolerance = db.Column(db.String(10))
    monthlySaving = db.Column(db.Float)
    cashBurn = db.Column(db.Float)
    debt = db.Column(db.Float)
    annualIncome = db.Column(db.Float)
    preferenceOfIncome = db.Column(db.String(10))

    def __init__(self, investorId, advisorId, rt, ms, cb, debt, ai, poi):
        self.investorId = investorId
        self.advisorId = advisorId
        self.riskTolerance = rt
        self.monthlySaving = ms
        self.cashBurn = cb
        self.debt = debt
        self.annualIncome = ai
        self.preferenceOfIncome = poi

class SurveySchema(marsh.Schema):
    class Meta:
        fields = ('investorId', 'advisorId', 'riskTolerance', 'monthlySaving', 'cashBurn', 'debt', 'annualIncome', 'preferenceOfIncome')

survey_schema = SurveySchema()
surveys_schema = SurveySchema(many=True)

@app.route('/investor/<investorId>/survey', methods=['POST'])
def addSurvey(investorId):
    rt = request.json['riskTolerance']
    ms = request.json['monthlySavings']
    cb = request.json['cashBurn']
    debt = request.json['debt']
    ai = request.json['annualIncome']
    poi = request.json['preferenceOfIncome']

    investor = Investor.query.get(investorId)

    survey = Survey(investor.investorId, investor.advisorId, rt, ms, cb, debt, ai, poi)

    db.session.add(survey)
    db.session.commit()

    return survey_schema.jsonify(survey)

@app.route('/investor/<investorId>/survey', methods=['GET'])
def getSurvey(investorId):
    survey = Survey.query.get(investorId)
    return survey_schema.jsonify(survey)

############################################################# Account CLASS ####################################################################################################
class Account(db.Model):
    accountId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    isAdvisor = db.Column(db.Boolean)
    userInv = db.relationship('Investor', backref='account', lazy=True)
    userAdv = db.relationship('Advisor', backref='account', lazy=True)

    def __init__(self, username, password, isAdvisor):
        self.username = username
        self.password = password
        self.isAdvisor = isAdvisor
    
    class AccountSchema(marsh.Schema):
        class Meta:
            fields = ('accountId', 'username', 'isAdvisor')
    
    account_schema = AccountSchema()
    accounts_schema = AccountSchema(many=True)

############################################################# Company CLASS/ENTITY ####################################################################################################
class Company(db.Model):
    companyName = db.Column(db.String(50), primary_key=True)
    industry = db.Column(db.String(30))
    sharesOutstanding = db.Column(db.Integer)
    marketCap = db.Column(db.Integer)
    offeredStock = db.relationship('Stock', backref='company', lazy=True)

    def __init__(self, name, industry, sot, mc):
        self.companyName = name
        self.industry = industry
        self.sharesOutstanding = sot
        self.marketCap = mc

# Company Schema
class CompanySchema(marsh.Schema):
        class Meta:
            fields = ('companyName', 'industry', 'sharesOutstanding', 'marketCap')

# Init the Schema
company_schema = CompanySchema()
companies_schema = CompanySchema(many=True)

# Add a Company to the database
@app.route('/company', methods=['POST'])
def addCompany():
    companyName = request.json['companyName']
    industry = request.json['industry']
    sharesOutstanding = request.json['sharesOutstanding']
    marketCap = request.json['marketCap']

    newCompany = Company(companyName, industry, sharesOutstanding, marketCap)

    db.session.add(newCompany)
    db.session.commit()

    return company_schema.jsonify(newCompany)

# Get a single Company
@app.route('/company/<companyName>', methods=['GET'])
def getCompany(companyName):
    company = Company.query.get(companyName)
    return company_schema.jsonify(company)

# Get all the companies in the database
@app.route('/company', methods=['GET'])
def getAllCompanies():
    allCompanies = Company.query.all()
    result = companies_schema.dump(allCompanies)
    return jsonify(allCompanies)

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

############################################################# Stock Class ########################################################################################################
class Stock(db.Model):
    ticker = db.Column(db.String(8), primary_key=True)
    currentPrice = db.Column(db.Float(2))
    targetPrice = db.Column(db.Float(2))
    companyName = db.Column(db.String(50), db.ForeignKey('company.companyName'))

    def __init__(self, tick, cPrice, tPrice, name):
        self.ticker = tick
        self.currentPrice = cPrice
        self.targetPrice = tPrice
        self.companyName = name


# Stock Schema
class StockSchema(marsh.Schema):
    class Meta:
        fields = ('ticker', 'currentPrice', 'targetPrice', 'companyName')

# Init the Schema, only deal with 1 individual stock per company
stock_schema = StockSchema()

# adding the stock to a company
@app.route('/company/<companyName>/stock', methods=['POST'])
def addStockToCompany(companyName):
    company = Company.query.get(companyName)
    ticker = request.json['ticker']
    currentPrice = request.json['currentPrice']
    targetPrice = request.json['targetPrice']
    companyName = companyName

    newStock = Stock(ticker, currentPrice, targetPrice, companyName)

    db.session.add(newStock)
    db.session.commit()
    return stock_schema.jsonify(newStock)

# getting the stock of a company
@app.route('/company/<companyName>/stock/<ticker>', methods=['GET'])
def getCompanyStock(companyName, ticker):
    stock = Stock.query.get(ticker)
    if stock.companyName != companyName:
        return stock_schema.jsonify(False)    # return an empty json since the company names must match, so no record on our database for unmatching company names
    else:
        return stock_schema.jsonify(stock)

# Updating the stock of a company
@app.route('/company/<companyName>/stock/<ticker>', methods=['PUT'])
def updateCompanyStock(companyName, ticker):
    stock = Stock.query.get(ticker)
    if companyName == stock.companyName:
        ticker = request.json['ticker']
        currentPrice = request.json['currentPrice']
        targetPrice = request.json['targetPrice']

        stock.ticker = ticker
        stock.currentPrice = currentPrice
        stock.targetPrice = targetPrice

        db.session.commit()
        return stock_schema.jsonify(stock)
    
    else:
        return stock_schema.jsonify(False)    # return an empty json since the company names must match, so no record on our database for unmatching company names

# Deleting the stock of a company
@app.route('/company/<companyName>/stock/<ticker>', methods=['DELETE'])
def deleteCompanyStock(companyName, ticker):
    stock = Stock.query.get(ticker)
    if companyName == stock.companyName:
        db.session.delete(stock)
        db.session.commit()
        return stock_schema.jsonify(stock)
    else:
        return stock_schema.jsonify(False)    # return an empty json since the company names must match, so no record on our database for unmatching company names
    

############################################################# News Class #########################################################################################################
class News(db.Model):
    headline = db.Column(db.String(100), primary_key=True)
    postedDate = db.Column(db.String(30))
    articleBody = db.Column(db.String)

    def __init__(self, title, date, body):
        self.headline = title
        self.postedDate = date
        self.articleBody = body

# News schema
class NewsSchema(marsh.Schema):
    class Meta:
        fields = ('headline', 'postedDate', 'articleBody')

class HeadlineSchema(marsh.Schema):
    class Meta:
        fields = ('headline',)

# Init the Schema
news_schema = NewsSchema()
multiple_news_schema = NewsSchema(many=True)
headlines_schema = HeadlineSchema(many=True)

# Adding a news item
@app.route('/news', methods=['POST'])
def addNewsItem():
    headline = request.json['headline']
    postedDate = request.json['postedDate']
    articleBody = request.json['articleBody']

    newNewsItem = News(headline, postedDate, articleBody)
    db.session.add(newNewsItem)
    db.session.commit()
    return news_schema.jsonify(newNewsItem)

# getting a news item
@app.route('/news/<headline>', methods=['GET'])
def getNewsItem(headline):
    newsItem = News.query.get(headline)
    return news_schema.jsonify(newsItem)

@app.route('/news/c:<companyName>', methods=['GET'])
def getByCompanyName(companyName):
    headlines = News.query.with_entities(News.headline).filter(News.headline.ilike('%' + companyName + '%'))
    result = headlines_schema.jsonify(headlines)
    return jsonify(articles=result.get_json())

@app.route('/news/t:<ticker>', methods=['GET'])
def getByTicker(ticker):
    headlines = News.query.with_entities(News.headline).filter(News.headline.like('%' + ticker + '%'))
    result = headlines_schema.jsonify(headlines)
    return jsonify(articles=result.get_json())

# deleting a News item
@app.route('/news/<headline>', methods=['DELETE'])
def deleteNewsItem(headline):
    newsItem = News.query.get(headline)
    db.session.delete(newsItem)
    db.session.commit()
    return news_schema.jsonify(newsItem)



############################################################# Portfolio Class ####################################################################################################
class Portfolio(db.Model):

    portfolioId = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=True)
    investorId = db.Column(db.Integer, db.ForeignKey('investor.investorId'))

    bonds = db.relationship('Portfolio_Bond', backref='portfolio', lazy=True)
    canadianEquities = db.relationship('Portfolio_Canadian_Equity', backref='portfolio', lazy=True)
    usEquities = db.relationship('Portfolio_US_Equity', backref='portfolio', lazy=True)

    def __init__(self, investorId):
        self.investorId = investorId

# Portfolio Schema
class PortfolioSchema(marsh.Schema):
        class Meta:
            fields = ('portfolioId', 'value', 'investorId')



# Init the Schema
portfolio_schema = PortfolioSchema()
portfolios_schema = PortfolioSchema(many=True)


# Create a portfolio

@app.route('/portfolio', methods=['POST'])
def addPortfolio():
    investorId = request.json['investorId']
    bonds = request.json['bonds']
    canadianEquities = request.json['canadianEquities']
    usEquities = request.json['usEquities']


    newPortfolio = Portfolio(investorId)
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

@app.route('/portfolio/<investorId>', methods=['GET'])
def getAccountPortfolios(investorId):
    portfolios = Portfolio.query.filter_by(investorId = investorId).all()
    result = portfolios_schema.jsonify(portfolios)
    return jsonify(portfolios=result.get_json())

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
    report = db.relationship('Report', backref='investment', lazy=True)

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

@app.route('/investment/invest/<referenceId>', methods=['PUT'])
def investIn(referenceId):
    investorId = request.json['investorId']
    investmentOption = Investment_Option.query.get(referenceId)
    newInvestment = Investment(referenceId, investorId, investmentOption.companyName, calculateMarketValue(investmentOption))
    db.session.add(newInvestment)
    db.session.delete(investmentOption)
    db.session.commit()
    return investment_schema.jsonify(newInvestment)

def calculateMarketValue(option):
    individualValue = Investment_Option.query.\
            filter_by(referenceId = option.referenceId).\
            join(Company).\
            join(Stock).\
            with_entities(Stock.currentPrice).\
            first()
    
    return individualValue.currentPrice * option.amount


@app.route('/investment/<referenceId>', methods=['DELETE'])
def deleteInvestment(referenceId):
    investment = Investment.query.get(referenceId)
    db.session.delete(investment)
    db.session.commit()
    return investment_schema.jsonify(investment)

class Investment_Option(db.Model):

    referenceId = db.Column(db.Integer, primary_key=True)
    advisorId = db.Column(db.Integer, db.ForeignKey('advisor.advisorId'))
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
            fields = ('referenceId', 'advisorId', 'amount', 'companyName', 'invType')


# Init the Schema
investment_option_schema = Investment_OptionSchema()
investment_options_schema = Investment_OptionSchema(many=True)

@app.route('/investment/options', methods=['POST'])
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

####################################################### Report CLASS ##############################################################################################
class Report(db.Model):
    referenceId = db.Column(db.Integer, db.ForeignKey('investment.referenceId'), primary_key=True)
    weeklyPerformance = db.Column(db.Float, nullable=True)
    monthlyPerformance = db.Column(db.Float, nullable=True)
    quarterlyPerformance = db.Column(db.Float, nullable=True)
    annualPerformance = db.Column(db.Float, nullable=True)
    fiveYearPerformance = db.Column(db.Float, nullable=True)
    sinceInceptionPerformance = db.Column(db.Float, nullable=True)

    def __init__(self, referenceId, wp, mp, qp, ap, fyp, sip):
        self.referenceId = referenceId
        self.weeklyPerformance = wp
        self.monthlyPerformance = mp
        self.quarterlyPerformance = qp
        self.annualPerformance = ap
        self.fiveYearPerformance = fyp
        self.sinceInceptionPerformance = sip

class Report_Schema(marsh.Schema):
    class Meta:
        fields = ('referenceId', 'weeklyPerformance', 'monthlyPerformance', 'quarterlyPerformance', 'annualPerformance', 'fiveYearPerformance', 'sinceInceptionPerformance')

report_schema = Report_Schema()
reports_schema = Report_Schema(many=True)

@app.route('/report', methods=['POST'])
def addReport():
    referenceId = request.json['referenceId']
    wp = request.json['weekly']
    mp = request.json['monthly']
    qp = request.json['quarterly']
    ap = request.json['annual']
    fyp = request.json['fiveYear']
    sip = request.json['sinceInception']

    newReport = Report(referenceId, wp, mp, qp, ap, fyp, sip)
    db.session.add(newReport)
    db.session.commit()

    return report_schema.jsonify(newReport)

@app.route('/report/<referenceId>', methods=['GET'])
def getReport(referenceId):
    report = Report.query.get(referenceId)
    return report_schema.jsonify(report)

@app.route('/report/<referenceId>', methods=['PUT'])
def updateReport(referenceId):
    report = Report.query.get(referenceId)
    wp = request.json['weekly']
    mp = request.json['monthly']
    ap = request.json['annual']
    fyp = request.json['fiveYear']
    sip = request.json['sinceInception']

    report.weeklyPerformance = wp
    report.monthlyPerformance = mp
    report.annualPerformance = ap
    report.fiveYearPerformance = fyp
    report.sinceInceptionPerformance = sip
    
    db.session.commit()

    return report_schema.jsonify(report)
####################################################### ADVISOR CLASS ##############################################################################################
class Advisor(db.Model):

    advisorId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    accountId = db.Column(db.Integer, db.ForeignKey('account.accountId'))
    qualifications = db.relationship('Advisor_Qualification', backref='advisor', lazy=True)
    investmentOptions = db.relationship('Investment_Option', backref='advisor', lazy=True)
    clients = db.relationship('Investor', backref='advisor', lazy=True)
    surveys = db.relationship('Survey', backref='advisor', lazy=True)

    def __init__(self, name, accountId):
        self.name = name
        self.accountId = accountId

# Advisor Schema
class AdvisorSchema(marsh.Schema):
        class Meta:
            fields = ('advisorId', 'name', 'accountId')

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

  newAccount = Account(username, password, True)
  db.session.add(newAccount)
  db.session.commit()

  newAdvisor = Advisor(name, newAccount.accountId)
  db.session.add(newAdvisor)
  db.session.commit()

  for x in qualifications:
      newQualification = Advisor_Qualification(newAdvisor.advisorId, x)
      db.session.add(newQualification)

  db.session.commit()

  return advisor_schema.jsonify(newAdvisor)

#get a single advisor via advisorId
@app.route('/advisor/<advisorId>', methods = ['GET'])
def getAdvisor(advisorId):
  advisor = Advisor.query.get(advisorId)
  return advisor_schema.jsonify(advisor)

#get qualifications of an advisor
@app.route('/advisor/<advisorId>/qualifications', methods = ['GET'])
def getAdvisorQualifications(advisorId):
  quals = Advisor_Qualification.query.filter_by(advisorId = advisorId).all()
  res = advisor_qualifications_schema.jsonify(quals)
  return jsonify(qualifications=res.get_json())

#get all advisors
@app.route('/advisor', methods = ['GET'])
def getAllAdvisors():
  allAdvisors = Advisor.query.all()
  result = advisors_schema.jsonify(allAdvisors)
  return jsonify(advisors=result.get_json())

# GET/advisor/{advisorId}/investors
#retrueve the list of investors an advisor is advertising
@app.route('/advisors/<advisorId>/investors', methods = ['GET'])
def getAdvisedInvestors(advisorId):
  AdvisedInvestors = Investor.query.filter_by(advisorId = (Advisor.query.get(advisorId))).all()
  result = investors_schema.jsonify(AdvisedInvestors)
  return jsonify(investors=result.get_json())

#update advisors 
@app.route('/advisor/<advisorId>', methods = ['PUT'])
def updateAdvisor(advisorId):
  advisor = Advisor.query.get(advisorId)
  name = request.json['name']
  password = request.json['password']
  qualifications = request.json['qualifications']

  account = Account.query.get(advisor.accountId)
  
  advisor.name = name
  account.password = password

  for x in qualifications:
      newQualification = Advisor_Qualification(advisor.advisorId, x)
      db.session.add(newQualification)

  db.session.commit()

  return advisor_schema.jsonify(advisor)


#delete advisor
@app.route('/advisor/<advisorId>', methods = ['DELETE'])
def deleteAdvisor(advisorId):
  advisor = Advisor.query.get(advisorId)
  db.session.delete(advisor)
  db.session.commit()
  return advisor_schema.jsonify(advisor)    

####################################################### ADVISOR Qualification CLASS ##############################################################################################
class Advisor_Qualification(db.Model):
    advisorId = db.Column(db.Integer, db.ForeignKey('advisor.advisorId'), primary_key=True)
    qualification = db.Column(db.String(50), primary_key=True)

    def __init__(self, advisorId, qual):
        self.advisorId = advisorId
        self.qualification = qual

# Advisor Qualification Schema
class Advisor_QualificationSchema(marsh.Schema):
        class Meta:
            fields = ('advisorId', 'qualification')

advisor_qualification_schema = Advisor_QualificationSchema()
advisor_qualifications_schema = Advisor_QualificationSchema(many=True)

  



# Run server

if __name__ == '__main__':

    app.run(debug=True)
