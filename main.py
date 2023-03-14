import re
import ast
import copy
import click
import pickle
import paperclip
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from functools import partial


class PythonLiteralOption(click.Option):
	def type_cast_value(self, ctx, value):
		try:
			return ast.literal_eval(value)
		except Exception as e:
			raise click.BadParameter(value)


class ArgHolder(object):
	pass


@click.group()
def entrypoint():
	pass


@click.command()
@click.option("--type", default="inner")
@click.argument("left")
@click.argument("right")
@click.argument("newview")
@click.argument("leftcols")
@click.argument("rightcols")
@click.pass_context
def join(ctx, type, left, right, newview, leftcols, rightcols):
	""" Join two files based on a single common attribute

	LEFT: The name of the first view

	RIGHT: The name of the second view

	LEFTCOLS: Cols from the left to use the join on (left will always be the dominant naming)

	RIGHTCOLS: Cols from the right to use the join on

	TYPE: e.g. inner

	"""
	pass

# extracts from existing view
@click.group()
@click.argument("viewname")
@click.argument("newview")
@click.pass_context
def extract(ctx, viewname, newview):
	""" Extract text from an existing corpus

	VIEWNAME : The name of the view which is used.

	NEWVIEW : The name of the view which will be generated from the extract

	"""
	# persist common attributes to click
	ctx.obj = (viewname, newview)


@extract.command()
@click.option("--nooverlap", is_flag=True, default=False, help="Kwics will not overlap in their contexts, the first match only will count.")
@click.option("--keepdata", is_flag=True, default=True, help="Whether the kwics will be joined with all previous data.")
@click.option("--masterexpr", default=None, help="An optional master regex, where the keywords will be interpolated in, with <KEYWORD>")
@click.argument("keywords")
@click.argument("cols")
# TODO: add a window size argument
@click.pass_context
def kwic(ctx, nooverlap, keepdata, masterexpr, keywords, cols):
	""" Generates a set of matching keywords with surrounding contexts

	KEYWORDS: Filepath to a file of keywords (can be a list of regex expressions)

	COLS: If multiple columns are presented (comma separated in ""), they will be combined into a single text_dump

	"""
	viewname, newview = ctx.obj
	pass


@extract.command()
@click.option("--includetf", is_flag=True, default=False, help="Should word_tf (simple term frequency) be included?")
@click.option("--ranks", default=20, help="How many ranks should be generated?")
@click.option("--lang", default="german", help="Language to use for stopword removal")
@click.argument("groupby")
@click.argument("cols")
@click.pass_context
def ctfidf(ctx, includetf, ranks, lang, groupby, cols):
	viewname, newview = ctx.obj
	pass


@extract.command()
@click.option("--lang", default="german", help="Language to use for stopword removal")
@click.argument("groupby")
@click.argument("cols")
@click.pass_context
def similarity(ctx, lang, groupby, cols):
	viewname, newview = ctx.obj
	pass

@extract.command()
@click.argument("lbd")
@click.pass_context
def filterby(ctx, lbd):
	viewname, newview = ctx.obj
	pass


@extract.command()
@click.option("--printoutput", is_flag=True, default=False, help="Whether to print the output of the count.")
@click.option("--horizontal", is_flag=True, default=False, help="Only works for col<int>.")
@click.argument("cols")
@click.pass_context
def groupbycount(ctx, printoutput, horizontal, cols):
	viewname, newview = ctx.obj
	pass


@extract.command()
@click.option("--delim", default=", ", help="Only works for col<int>.")
@click.argument("groupbycols")
@click.argument("condensecols")
@click.pass_context
def groupbycondense(ctx, delim, groupbycols, condensecols):
	""" Condense text column(s) by grouping on col(s) """
	viewname, newview = ctx.obj
	pass

# insights from text
@click.group()
@click.option("--newview", default=None, help="Name of the new view, else column is appended / or view overwritten.")
@click.argument("feature")
@click.argument("viewname")
@click.pass_context
def utils(ctx, newview, feature, viewname):
	""" Perform a utility on a feature column to generate new features

	FEATURE : The name of the column the util will be performed on.

	VIEWNAME : The name of the view which is used.
	"""
	# persist common attributes to click
	ctx.obj = (newview, feature, viewname)

@utils.command()
@click.option("--modelname", default=None, help="An optional model name. Default XLM-roberta (Cardiffnlp)")
@click.pass_context
def sentiment(ctx, modelname):
	newview, feature, viewname = ctx.obj
	pass

@utils.command()
@click.option("--icol", default=None)
@click.option("--ival", default=None)
@click.option("--newcol", default=None)
@click.argument("source")
@click.argument("target")
@click.pass_context
def translate(ctx, icol, ival, newcol, source, target):
	""" Translate texts """
	newview, feature, viewname = ctx.obj
	pass


@utils.command()
@click.option("--cscol", default=None, help="Name of an inner column that indicated case sensitivity of the match. Default, case insensitive.")
@click.argument("nestedcolorder")
@click.argument("regexcol")
@click.argument("keywordsfile")
@click.pass_context
def matchcounter(ctx, cscol, nestedcolorder, regexcol, keywordsfile):
	""" Perform a matchcount operation """
	newview, feature, viewname = ctx.obj
	pass

# TODO: add fine tuning parameters
@utils.command()
@click.option("--includep", is_flag=True, help="Raise flag to include probability scores.")
@click.option("--clusterlb", default=15, help="min_cluster_size (HDB) (how small should the clusters be minimally?)")
@click.option("--samplelb", default=6, help="min_samples (how conservative should the clustering be?) (larger, more conservative)")
@click.pass_context
def hdbscan(ctx, includep, clusterlb, samplelb):
	""" Perform hdbscan on a desired text-vector representation """
	newview, feature, viewname = ctx.obj
	pass


@utils.command()
@click.option("--components", default=10, help="UMAP (number of dimension)")
@click.option("--neighbors", default=18, help="UMAP (low neightbors: focus on local structure)")
@click.option("--seed", default=42, help="A random seed for controlling consistency.")
@click.option("--dist",  default=0.1, help="UMAP (larger value: allow for broader topological structure / less clumps)")
@click.pass_context
def umap(ctx, components, neighbors, seed, dist):
	""" Perform umap on a desired text-vector representation """
	newview, feature, viewname = ctx.obj
	pass

# encode text into vector representations
@click.group()
@click.option("--newview", default=None, help="Name of the new view, else column is appended / or view overwritten.")
@click.option("--filepath", default=None, help="Specify a filepath if a view doesn't exist yet")
@click.argument("textcol")
@click.argument("viewname")
@click.pass_context
def encoder(ctx, newview, filepath, textcol, viewname):
	""" Encoders for encoding natural language text into vector-representation

	FILEPATH : Filepath to a file wanting to be loaded.

	TEXTCOL : The name of the csv column that holds text.

	VIEWNAME : The name of the view, to be created if from filebath, or to be used.
	"""
	ctx.obj = (newview, filepath, textcol, viewname)


@encoder.command()
@click.option("--modelname", default=None, help="SBERT model to be used")
@click.option("--multiprocessing", is_flag=True, default=False, help="Use multiprocessing?")
@click.option("--chunksize", default=None)
@click.option("--clip", default=None, help="Optional clipping parameter")
@click.pass_context
def sbert(ctx, modelname, multiprocessing, chunksize, clip):
	newview, filepath, textcol, viewname = ctx.obj
	pass

# multilabel vs. multiclass
# TODO: specify featureset (columns)
# TODO: specify label (if new, add new... if old, specify a NULL value)
@click.command()
@click.option("--newview", default=None, help="Name of the new view, else column is appended / or view overwritten.")
@click.option("--annotatorfile", default="oracle.csv", help="Choose the file which will query you for annotation")
# @click.option("--newlabelcolumn")
# @click.option("--criticalvalue", default=-1, )
@click.option("--nsuggest", default=5)
@click.option("--learnername", default="mylearner")
@click.option("--multilabel", is_flag=True, default=False)
@click.option("--binarize", is_flag=True, default=False)
@click.argument("features")
@click.argument("label")
@click.argument("viewname")
def train(newview, annotatorfile, nsuggest, learnername, multilabel, binarize, features, label, viewname):
	""" Initiate a training process on a chosen view.

	FEATURES: comma separated feature names / columns of the views (will be combined)

	LABEL: the label the model will be trained on
	"""
	pass



# multilabel vs. multiclass
@click.group()
def validate():
	""" Validate your sklearn model using features and a label

	FEATURES : comma separated feature names / columns (will be combined).

	LABEL : the label the model will be validated on.
	"""
	pass

@click.group()
@click.argument("view1")
@click.argument("view2")
@click.pass_context
def append(ctx, view1, view2):
	"""Append a column to another view"""
	ctx.obj = (view1, view2)

@append.command()
@click.option("--newcolname", default=None, help="Should the column be renamed before being appended?")
@click.argument("col")
# TODO: add a window size argument
@click.pass_context
def column(ctx, newcolname, col):
	""" Append column from view1 to view 2 """
	view1, view2 = ctx.obj
	pass


@click.group()
@click.argument("viewname")
@click.pass_context
def segment(ctx, viewname):
	"""Append a column to another view"""
	ctx.obj = (viewname)
	click.echo(viewname)

@segment.command()
@click.argument("viewname2")
@click.pass_context
def world(ctx, viewname2):
	view = ctx.obj
	click.echo(view)
	click.echo(viewname2)


@segment.command()
@click.argument("col")
@click.option("--newcolname", default=None, help="Should the column be renamed before being appended?")
@click.option("--nsent", default=8, help="Into how many sentences should the text per column be expanded?")
@click.pass_context
def sentencewise(ctx, col, newcolname, nsent):
	""" Given a table with a column of large texts per cells, split this into n-sentences (elongates the table) """
	view = ctx.obj
	view_data = vb(view).load()
	pass




# add different sub entrypoints
entrypoint.add_command(join)
entrypoint.add_command(extract)
entrypoint.add_command(utils)
entrypoint.add_command(encoder)
entrypoint.add_command(train)
entrypoint.add_command(validate)
entrypoint.add_command(append)
entrypoint.add_command(segment)

if __name__ == "__main__":
	entrypoint()