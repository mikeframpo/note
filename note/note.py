#!/usr/bin/python3

import argparse
from argparse import RawTextHelpFormatter
from pathlib import Path, PurePath
import sys
import os.path
import os
import itertools
from subprocess import call
from datetime import datetime
import platform

if platform.system() == 'Windows':
    NOTES_PATH = Path('m:/My Drive/Notes')
else:
    NOTES_PATH = Path.joinpath(Path.home(), 'Drive/Notes')

DISPLAY_LIMIT = 10

def do_new(args):
    cats = list(get_categories())
    for i, v in enumerate(cats):
        print('({}) {}'.format(i, str(v.relative_to(NOTES_PATH))))
    cat_num = int(input('Creating new notes file, select category folder\n'))
    
    dest_dir = cats[cat_num]
    desc = input('Enter note file name or space-separated tags\n')
    
    note_name = '{}-{}.md'.format(
        datetime.today().strftime('%y%m%d'),
        desc.replace(' ', '-'))
    note_dest = PurePath.joinpath(dest_dir, note_name)
    input('Creating new note with name {}, <Enter> to continue...'.format(
        note_dest))
    call_editor(note_dest)

def do_list(args):
    list_notes(args.pattern)

def do_edit(args):
    list_notes(args.pattern)
    note_num = int(input('Select notes file for editing\n'))
    
    notes_files = get_notes(DISPLAY_LIMIT, args.pattern)
    note = next(itertools.islice(notes_files, note_num, None))
    call_editor(note)

def do_list_categories(args):
    categories = get_categories()
    print('Listing {} categories in alphabetical order'.format(DISPLAY_LIMIT))
    for i, v in enumerate(categories):
        print('({}) {}'.format(i, str(v.relative_to(NOTES_PATH))))

def do_new_category(args):
    print('Enter path to new category in format: parent/new-category')
    cat_dir = input()
    new_category(cat_dir)

def list_notes(pattern=None):
    notes_files = get_notes(DISPLAY_LIMIT, pattern)
    print('Listing {} notes. Recently modified first'.format(DISPLAY_LIMIT))
    for i, v in enumerate(notes_files):
        print('({}) {}'.format(i, str(v.relative_to(NOTES_PATH))))

def get_notes(limit, pattern=None):
    notes_files = []
    walk_notes_dir(NOTES_PATH, notes_files, pattern=pattern)

    notes_files = reversed(sorted(notes_files, key=os.path.getmtime))
    return itertools.islice(notes_files, limit)

def get_categories():
    cats = []
    walk_notes_dir(NOTES_PATH, cats, False)
    cat_dirs = sorted(cats)
    return cat_dirs

def new_category(cat_dir):
    cat_path = PurePath.joinpath(NOTES_PATH, cat_dir)
    if cat_path.exists():
        print('Category {} already exists'.format(cat_dir))
        return
    try:
        cat_path.mkdir()
        print('Created category: {}'.format(cat_dir))
    except FileNotFoundError:
        print('Failed to create {}, make sure parent category exists'.format(cat_path))

def call_editor(note_file):
    editor = os.environ.get('NOTE_EDITOR')
    if editor is None:
        print('Warning: environment variable NOTE_EDITOR not set, defaulting to vim')
        editor = os.environ.get('EDITOR', 'vim')
    call([editor, note_file], shell=True)

def walk_notes_dir(path_elem, dest, files=True, pattern=None):
    if path_elem.is_dir():
        for child in path_elem.iterdir():
            if child.is_file() and child.suffix == '.md' \
                and (pattern is None or pattern in str(child)) \
                and files:

                dest.append(child)
            elif child.is_dir():
                if not files:
                    if pattern is None or pattern in str(child):
                        dest.append(child)
                walk_notes_dir(child, dest, files, pattern)

COMMANDS = {
    'new': do_new,
    'list': do_list,
    'edit': do_edit,
    'lcat': do_list_categories,
    'ncat': do_new_category,
}

def _main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    subp = parser.add_subparsers(dest='subparser')

    p_new = subp.add_parser('new', help='Create a new note')
    p_list = subp.add_parser('list', help='List existing notes')
    p_list.add_argument('pattern', nargs='?',
        help='Pattern to match against note name or category or categories')

    p_edit = subp.add_parser('edit', help='Edit an existing note')
    p_edit.add_argument('pattern', nargs='?',
        help='Pattern to match against note name or category or categories')
    p_lcat = subp.add_parser('lcat', help='List existing categories')
    p_ncat = subp.add_parser('ncat', help='Create a category')
    args = parser.parse_args()

    if not NOTES_PATH.exists():
        print('Warning: expected notes path {} does not exist'.format(NOTES_PATH))

    if args.subparser is None:
        print('positional argument is required')
        parser.print_help()
        sys.exit(1)

    # run the command
    COMMANDS[args.subparser](args)

