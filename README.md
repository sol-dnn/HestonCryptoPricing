# HestonCryptoPricing

## Overview  
This repository contains research and implementation of **Heston model calibration** for cryptocurrency option pricing. The project involves **data collection, volatility surface modeling, deep learning-based calibration, and risk-neutral option pricing**.  

## Features  
- **Database Creation**: Fetch and process live trading data using the **Deribit API**.  
- **Heston Pricer**: Implement the **Heston stochastic volatility model** for pricing crypto options.  
- **Deep Learning Calibration**: Train a neural network to optimize the Heston model parameters.  
- **Volatility Surface Analysis**: Fit and visualize implied volatility surfaces for BTC and ETH options.  
- **Optimization Techniques**: Use **Levenberg-Marquardt, Differential Evolution, and L2 regularization** for calibration.  

## Repository Structure  
```plaintext
HestonCryptoPricing/ 
│── database_creation/ # Collecting and processing crypto options data from Deribit API
│── src
  │── heston_pricer/ # Heston model implementation for option pricing
  │── deep_learning_calibration/ # Neural network-based calibration of Heston parameters
  │── heston_volatility_surface/ # Volatility surface fitting & visualization
│── project_report.pdf
│── related_papers        # All the references
│── README.md         # Project documentation
│── requirements.txt # Dependencies for running the code
```

## Installation  
To install the required dependencies, run:  
```bash
pip install -r requirements.txt

Usage
- Collect Data: Use the database_creation module to fetch BTC/ETH options data from Deribit API.
- Heston Calibration: Optimize the Heston model using traditional methods and deep learning.
- Option Pricing: Use the calibrated model to price crypto derivatives.
- Volatility Surface Analysis: Visualize and analyze implied volatilities.

This project explores:
- Comparing traditional vs. ML-based Heston calibration
- Analyzing volatility skew in crypto options
- Assessing the impact of regularization on parameter estimation

For detailed research and methodology, refer to the paper "Heston Model Calibration in the Cryptocurrency Market" (included in this repository).
