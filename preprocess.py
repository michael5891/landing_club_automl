"""
All rights reserved to cnvrg.io
     http://www.cnvrg.io

cnvrg.io - Projects Example

Written by: Omer Liberman

Last update: Oct 31, 2019
Updated by: Omer Liberman

preprocess.py
==============================================================================
"""
import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="""Preprocessor""")
parser.add_argument('--data', action='store', dest='data', required=True,
					help="""string. path to the raw dataset.""")
args = parser.parse_args()
data = args.data

# ---------------- Helpers --------------------
# Helper method - converts non-numbers to 0
def cast_all_non_numbers(col):
	"""
	:param col: data frame. shape=(col_len, 1)
	:return: the same column, but all non-numbers (nan, na, etc.) are 0.
	"""
	values = [None] * len(col)
	for ind in range(len(col)):
		val = 0.0
		try:
			val = float(col[ind])
		except ValueError:
			continue
		values[ind] = val
	return col


# Helper method - scale column.
def scale_column(col):
	"""
	:param col: data frame. shape=(col_len, 1)
	:return: the same column, but all scaled.
	"""
	df = col
	df -= df.min()
	df /= df.max()
	return df


# Helper method - emp_length/
def process_emp_length_col(col):
	values = [0] * len(col)
	terms_dict = {'< 1 year': 2, '1 year': 2, '2 years': 2, '3 years': 4, '4 years': 4, '5 years': 6, '6 years': 6,
				  '7 years': 8, '8 years': 8, '9 years': 10, '10+ years': 10}
	for ind in range(len(col)):
		try:
			values[ind] = int(terms_dict[col[ind]])
		except KeyError:
			continue
	return values


# ------------- Constants --------------------
# Features should be categorical features.
to_dummies = ["term", "grade", "home_ownership", "verification_status"]

# Features should be scaled.
to_scale = ["loan_amnt", "installment", "annual_inc", "dti", "revol_bal", "inq_last_6mths", "open_acc", "revol_util"]

# Features should be dropped.
to_drop = ["emp_title", "pymnt_plan", "desc", "purpose", "title", "zip_code", "addr_state", "delinq_2yrs",
		   "earliest_cr_line", "mths_since_last_record", "pub_rec", "total_acc", "initial_list_status",
		   "collections_12_mths_ex_med", "mths_since_last_delinq", "mths_since_last_major_derog", "policy_code",
		   "month_issued", "year_issued"]


# ------------- ------- --------------------
# Read dataset.
data = pd.read_csv(data)

# Target feature.
target_feature, is_target_feature_included, target_col = "is_bad", False, None
if target_feature in data.columns:
	is_target_feature_included = True
	target_col = data[target_feature]
	data = data.drop(columns=[target_feature], axis=1)

for column in data.columns:
	if column.startswith('Unnamed'):
		data = data.drop(columns=column, axis=1)

# Special treat.
special = ["emp_length"]

# Converting grade column. Ex: {A} ->{1}
con_dict = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7}
data['grade'] = data['grade'].map(con_dict)

# Converting sub_grade column. Ex: {A4} ->{4}
sub_grade_col = []
for i in range(len(data['sub_grade'])):
	ch = data['sub_grade'][i][1]
	sub_grade_col.append(int(ch))
data['sub_grade'] = sub_grade_col

# Converting inq_last_6mths
new_inq_last_6mths = cast_all_non_numbers(data['inq_last_6mths'])
data = data.drop(columns=['inq_last_6mths'], axis=1)
data['inq_last_6mths'] = new_inq_last_6mths

# Converting open_acc
new_open_acc = cast_all_non_numbers(data['open_acc'])
data = data.drop(columns=['open_acc'], axis=1)
data['open_acc'] = new_open_acc

# Converting revol_util
new_revol_util = cast_all_non_numbers(data['revol_util'])
data = data.drop(columns=['revol_util'], axis=1)
data['revol_util'] = new_revol_util

# Drop.
data = data.drop(columns=to_drop, axis=1)

# Scaling.
for col_to_scale in to_scale:
	scaled = scale_column(data[col_to_scale])
	data = data.drop(columns=[col_to_scale], axis=1)
	data[col_to_scale] = scaled

# Categorical features.
data = pd.get_dummies(data, columns=to_dummies)

# Process emp_length col.
emp_length_new = process_emp_length_col(data['emp_length'])
data = data.drop(columns=['emp_length'], axis=1)
data['emp_length'] = emp_length_new

# Last - na dropouts.
data = data.fillna(0)

final_columns = ['int_rate', 'sub_grade', 'loan_amnt', 'installment', 'annual_inc',
				 'dti', 'revol_bal', 'inq_last_6mths', 'open_acc', 'revol_util',
				 'term_ 36 months', 'term_ 60 months', 'grade_1', 'grade_2', 'grade_3',
				 'grade_4', 'grade_5', 'grade_6', 'grade_7', 'home_ownership_MORTGAGE', 'home_ownership_OTHER', 'home_ownership_OWN',
				 'home_ownership_NONE', 'home_ownership_RENT', 'verification_status_VERIFIED - income',
				 'verification_status_VERIFIED - income source',
				 'verification_status_not verified', 'emp_length']

if is_target_feature_included:
	data[target_feature] = target_col
	final_columns.append('is_bad')

data.columns = final_columns

# Pushing the processed data set to a new cnvrg data set using cnvrg-CLI.
if not os.path.exists('example-lendingclub'):
	os.mkdir('example-lendingclub')
data.to_csv('example-lendingclub/processed_data_set.csv')
os.system("cd example-lendingclub && cnvrg data init && cnvrg data sync")