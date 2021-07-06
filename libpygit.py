import collections
import configparser
import hashlib
import os
import re
import sys
import zlib

import click

from commands import cmd_init

@click.group()
def cmd():
    pass

@cmd.command()
@click.argument('path', required=False)
def init(path: str):
  cwd = os.getcwd()
  if not path:
    path = cwd
  else:
    path = os.path.join(cwd, path)

  cmd_init.run(path)

@cmd.command()
def add():
  click.echo('add')


@cmd.command(name='cat-file')
def cat_file():
  click.echo('cat-file')

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
