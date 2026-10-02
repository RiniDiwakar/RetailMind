# RetailMind

### Predict. Understand. Personalize.

RetailMind is an AI-powered retail intelligence platform that analyzes customer transaction data to understand customer behavior and provide actionable business insights.

## Features

- Customer Segmentation
- Customer Churn Prediction
- Next Best Action recommendations

## Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- Flask
- Flask-CORS
- SQLite
- HTML
- CSS
- JavaScript

## Project Structure

- `backend/` - Flask backend and APIs
- `frontend/` - Web interface
- `ml/` - Machine learning code
- `models/` - Trained ML models
- `tests/` - Automated tests

## Dataset Format

The uploaded CSV should contain:

`customer_id`, `invoice`, `purchase_date`, `quantity`, `amount`

Example:

```csv
customer_id,invoice,purchase_date,quantity,amount
C001,10001,2011-01-05,2,500
C001,10002,2011-02-10,1,300
C002,10003,2011-02-15,4,1200