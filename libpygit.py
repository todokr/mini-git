import collections
import configparser
import hashlib
import os
import re
import sys
import zlib

import click

import commands
from models import GitRepository

@click.group()
def cmd():
    pass

@cmd.command()
@click.argument('path', required=False)
def init(path: str):
    cwd = os.getcwd()
    if not path:
        p = cwd
    else:
        p = os.path.join(cwd, path)

    commands.run_init(p)


@cmd.command(name='cat-file')
@click.argument('sha')
def cat_file(sha: str):
    result = commands.run_cat_file(os.getcwd(), sha)
    click.echo(result)

@cmd.command(name='hash-object')
@click.option('--type', '-t', type=click.Choice(['blob', 'commit', 'tag', 'tree']), default='blob')
@click.option('--write', '-w', type=bool, default=False)
@click.argument('file', type=str, required=True)
def hash_object(type, write, file):
    sha = commands.run_hash_object(os.getcwd(), type, write, file)
    click.echo(sha)

@cmd.command(name='log')
@click.argument('sha')
def log(sha):
    commands.run_log(os.getcwd(), sha)

@cmd.command()
def add():
  click.echo('add')


@cmd.command()
def checkout():
  click.echo('checkout')

@cmd.command()
def commit():
  click.echo('commit')

@cmd.command(name='ls-tree')
def ls_tree():
  click.echo('ls-tree')

@cmd.command()
def merge():
  click.echo('merge')

@cmd.command()
def rebase():
  click.echo('rebase')

@cmd.command(name='rev-parse')
def rev_parse():
  click.echo('rev-parse')

@cmd.command()
def rm():
  click.echo('rm')

@cmd.command(name='show-ref')
def show_ref():
  click.echo('show-ref')

@cmd.command()
def tag():
  click.echo('tag')
