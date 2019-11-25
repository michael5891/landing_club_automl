"""
All rights reserved to cnvrg.io
     http://www.cnvrg.io

cnvrg.io - AI library

Written by: Omer Liberman

Last update: Oct 06, 2019
Updated by: Omer Liberman

xgb.py
==============================================================================
"""
import argparse
import pickle

import pandas as pd
from cnvrg import Experiment
from sklearn.metrics import accuracy_score, mean_squared_error

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, KFold

import warnings
warnings.filterwarnings(action="ignore", category=RuntimeWarning)
warnings.filterwarnings(action='ignore', category=DeprecationWarning)

def _cast_types(args):
	"""
	This method performs casting to all types of inputs passed via cmd.
	:param args: argparse.ArgumentParser object.
	:return: argparse.ArgumentParser object.
	"""
	# x_val.
	if args.x_val != 'None':
		args.x_val = int(args.x_val)
	else:
		args.x_val = None

	# test_size
	args.test_size = float(args.test_size)

	# learning_rate.
	args.learning_rate = float(args.learning_rate)

	# n_estimators.
	args.n_estimators = int(args.n_estimators)

	# silent.
	args.silent = (args.silent == 'True' or args.silent == "True")

	# n_jobs.
	if args.n_jobs == "None" or args.n_jobs == 'None':
		args.n_jobs = None
	else:
		args.n_jobs = int(args.n_jobs)

	# nthread.
	if args.nthread == "None" or args.nthread == 'None':
		args.nthread = None
	else:
		args.nthread = int(args.nthread)

	# gamma.
	args.gamma = int(args.gamma)

	# min_child_weight.
	args.min_child_weight = int(args.min_child_weight)

	# max_delta_step.
	args.max_delta_step = int(args.max_delta_step)

	# subsample.
	args.subsample = int(args.subsample)

	# colsample_bytree.
	args.colsample_bytree = int(args.colsample_bytree)

	# colsample_bylevel.
	args.colsample_bylevel = int(args.colsample_bylevel)

	# reg_alpha.
	args.reg_alpha = int(args.reg_alpha)

	# reg_lambda.
	args.reg_lambda = int(args.reg_lambda)

	# scale_pos_weight.
	args.scale_pos_weight = int(args.scale_pos_weight)

	# base_score.
	args.base_score = float(args.base_score)

	# random_state.
	args.random_state = int(args.random_state)

	# seed.
	if args.seed == "None" or args.seed == 'None':
		args.seed = None
	else:
		args.seed = int(args.seed)

	# missing.
	if args.missing == "None" or args.missing == 'None':
		args.missing = None

	return args


def train_with_cross_validation(model, train_set, test_set, folds, project_dir, output_model_name):
	train_acc, train_loss = [], []
	kf = KFold(n_splits=folds)
	X, y = train_set
	# --- Training.
	for train_index, val_index in kf.split(X):
		X_train, X_val = X.iloc[train_index, :], X.iloc[val_index, :]
		y_train, y_val = y.iloc[train_index], y.iloc[val_index]
		model.fit(X_train, y_train)
		model.n_estimators += 1
		y_hat = model.predict(X_val)  # y_hat is a.k.a y_pred
		acc = accuracy_score(y_val, y_hat)
		loss = mean_squared_error(y_val, y_hat)

		train_acc.append(acc)
		train_loss.append(loss)
	# --- Testing.
	X_test, y_test = test_set
	y_pred = model.predict(X_test)
	test_acc = accuracy_score(y_test, y_pred)
	test_loss = mean_squared_error(y_test, y_pred)

	exp = Experiment()
	exp.log_param("model", output_model_name)
	exp.log_param("folds", folds)
	exp.log_metric("train_acc", train_acc)
	exp.log_metric("train_loss", train_loss)
	exp.log_param("test_acc", test_acc)
	exp.log_param("test_loss", test_loss)

	# Save model.
	output_file_name = project_dir + "/" + output_model_name if project_dir is not None else output_model_name
	pickle.dump(model, open(output_file_name, 'wb'))


def train_without_cross_validation(model, train_set, test_set, project_dir, output_model_name):
	X_train, y_train = train_set
	# --- Training.
	model.fit(X_train, y_train)
	y_hat = model.predict(X_train)  # y_hat is a.k.a y_pred

	train_acc = accuracy_score(y_train, y_hat)
	train_loss = mean_squared_error(y_train, y_hat)
	# --- Testing.
	X_test, y_test = test_set
	y_pred = model.predict(X_test)
	test_acc = accuracy_score(y_test, y_pred)
	test_loss = mean_squared_error(y_test, y_pred)

	exp = Experiment()
	exp.log_param("model", output_model_name)
	exp.log_param("train_acc", train_acc)
	exp.log_param("train_loss", train_loss)
	exp.log_param("test_acc", test_acc)
	exp.log_param("test_loss", test_loss)

	# Save model.
	output_file_name = project_dir + "/" + output_model_name if project_dir is not None else output_model_name
	pickle.dump(model, open(output_file_name, 'wb'))

def main(args):
	args = _cast_types(args)

	# Loading data set.
	data = pd.read_csv(args.data)
	for col in data.columns:
		if col.startswith('Unnamed'):
			data = data.drop(columns=col, axis=1)

	# Checking data sets sizes.
	rows_num, cols_num = data.shape
	if rows_num == 0:
		raise Exception("Library Error: The given dataset has no examples.")
	if cols_num < 2:
		raise Exception("Dataset Error: Not enough columns.")

	# Split to X and y.
	X = data.iloc[:, :-1]
	y = data.iloc[:, -1]

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_size)

	# Model initialization.
	model = XGBClassifier(
		max_depth=args.max_depth,
		learning_rate=args.learning_rate,
		n_estimators=args.n_estimators,
		silent=args.silent,
		objective=args.objective,
		booster=args.booster,
		n_jobs=args.n_jobs,
		nthread=args.nthread,
		gamma=args.gamma,
		min_child_weight=args.min_child_weight,
		max_delta_step=args.max_delta_step,
		subsample=args.subsample,
		colsample_bytree=args.colsample_bytree,
		colsample_bylevel=args.colsample_bylevel,
		reg_alpha=args.reg_alpha,
		reg_lambda=args.reg_lambda,
		scale_pos_weight=args.scale_pos_weight,
		base_score=args.base_score,
		random_state=args.random_state,
		seed=args.seed,
		missing=args.missing
	)

	# Training with cross validation.
	if args.x_val is not None:
		train_with_cross_validation(model=model,
									train_set=(X_train, y_train),
									test_set=(X_test, y_test),
									folds=args.x_val,
									project_dir=args.project_dir,
									output_model_name=args.output_model)

	# Training without cross validation.
	else:
		train_without_cross_validation(model=model,
										train_set=(X_train, y_train),
										test_set=(X_test, y_test),
										project_dir=args.project_dir,
										output_model_name=args.output_model)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="""xgboost Classifier""")

	# ----- cnvrg.io params.
	parser.add_argument('--data', action='store', dest='data', required=True,
	                    help="""String. path to csv file: The data set for the classifier. Assumes the last column includes the labels. """)

	parser.add_argument('--project_dir', action='store', dest='project_dir',
	                    help="""--- For inner use of cnvrg.io ---""")

	parser.add_argument('--output_dir', action='store', dest='output_dir',
	                    help="""--- For inner use of cnvrg.io ---""")

	parser.add_argument('--x_val', action='store', default="None", dest='x_val',
	                    help="""Integer. Number of folds for the cross-validation. Default is None.""")

	parser.add_argument('--test_size', action='store', default="0.2", dest='test_size',
	                    help="""Float. The portion of the data of testing. Default is 0.2""")

	parser.add_argument('--output_model', action='store', default="xgb_model.sav", dest='output_model',
	                    help="""String. The name of the output file which is a trained random forests model """)

	# ----- model's params.
	parser.add_argument('--max_depth', action='store', default="3", dest='max_depth',
						help=""" --- .Default is 3""")

	parser.add_argument('--learning_rate', action='store', default="0.1", dest='learning_rate',
						help=""" --- .Default is 0.1""")

	parser.add_argument('--n_estimators', action='store', default="100", dest='n_estimators',
						help=""": --- . Default is 100""")

	parser.add_argument('--silent', action='store', default="True", dest='silent',
						help=""": --- . Default is True""")

	parser.add_argument('--objective', action='store', default='binary:logistic', dest='objective',
						help=""": --- . Default is 'binary:logistic'""")

	parser.add_argument('--booster', action='store', default='gbtree', dest='booster',
						help=""": --- . Default is 'gbtree'""")

	parser.add_argument('--n_jobs', action='store', default="1", dest='n_jobs',
						help=""": --- . Default is 1""")
	# Check Type
	parser.add_argument('--nthread', action='store', default="None", dest='nthread',
						help=""": --- . Default is None""")

	parser.add_argument('--gamma', action='store', default="0", dest='gamma',
						help=""": --- . Default is 0""")

	parser.add_argument('--min_child_weight', action='store', default="1", dest='min_child_weight',
						help=""": --- . Default is 1""")

	parser.add_argument('--max_delta_step', action='store', default="0", dest='max_delta_step',
						help=""": --- . Default is 0""")

	parser.add_argument('--subsample', action='store', default="1", dest='subsample',
						help=""": --- . Default is 1""")

	parser.add_argument('--colsample_bytree', action='store', default="1", dest='colsample_bytree',
						help=""": --- . Default is 1""")

	parser.add_argument('--colsample_bylevel', action='store', default="1", dest='colsample_bylevel',
						help=""": --- . Default is 1""")

	parser.add_argument('--reg_alpha', action='store', default="0", dest='reg_alpha',
						help=""": --- . Default is 0""")

	parser.add_argument('--reg_lambda', action='store', default="1", dest='reg_lambda',
						help=""": --- . Default is 1""")

	parser.add_argument('--scale_pos_weight', action='store', default="1", dest='scale_pos_weight',
						help=""": --- . Default is 1""")

	parser.add_argument('--base_score', action='store', default="0.5", dest='base_score',
						help=""": --- . Default is 0.5""")

	parser.add_argument('--random_state', action='store', default="0", dest='random_state',
						help=""": --- . Default is 0""")

	# Type
	parser.add_argument('--seed', action='store', default="None", dest='seed',
						help=""": --- . Default is None""")
	# Type
	parser.add_argument('--missing', action='store', default="None", dest='missing',
						help=""": --- . Default is None""")

	args = parser.parse_args()

	main(args)
