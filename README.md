# Phantom Mask Pharmacy Backend

## Introduction
A backend RESTful API service for pharmacy management, written in Python Flask and SQLite.

## Setup
1. Clone the repo
2. Run `python etl.py`
3. Run `python app.py`

## Features
- 1.List all pharmacies open at a specific time and on a day of the week if requested.
- 2.List all masks sold by a given pharmacy, sorted by mask name or price.
- 3.List all pharmacies with more or less than x mask products within a price range.
- 4.The top x users by total transaction amount of masks within a date range.
- 5.The total number of masks and dollar value of transactions within a date range.
- 6.Search for pharmacies or masks by name, ranked by relevance to the search term.
- 7.Process a user purchases a mask from a pharmacy, and handle all relevant data changes in an atomic transaction.
## test
- 本專案已撰寫 pytest 測試並以 coverage 產生報告，總測試覆蓋率 85%。各主要功能的 API 均有自動化測試，確保品質與穩定性。