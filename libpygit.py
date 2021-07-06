import collections
import configparser
import hashlib
import os
import re
import sys
import zlib

import click

from commands import cmd_init
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

  cmd_init.run(p)


@cmd.command(name='cat-file')
@click.argument('sha')
def cat_file(sha: str):
  repo = GitRepository.load(os.getcwd())
  obj = repo.load_object(sha)
  click.echo(obj.serialize().decode('utf-8'))

@cmd.command()
def add():
  click.echo('add')


@cmd.command()
def checkout():
  click.echo('checkout')

@cmd.command()
def commit():
  click.echo('commit')

@cmd.command(name='hash-object')
def hash_object():
  click.echo('hash-object')

@cmd.command()
def log():
  click.echo('log')

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
