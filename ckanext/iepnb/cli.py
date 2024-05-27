# -*- coding: utf-8 -*-

from __future__ import print_function

import click
import logging

import ckanext.schemingdcat.cli as sdct_cli
import ckanext.iepnb.config as iepnb_config

log = logging.getLogger(__name__)


def get_commands():
    return [iepnb]

@click.group()
def iepnb():
    """
    This is the main entry point for the CLI. It groups all the iepnb commands together.
    """
    pass
   
@iepnb.command()
@click.option("-l", "--lang", default="es", show_default=True)
def create_iepnb_tags(lang):
    """
    This command creates the IEPNB Keywords vocabulary.

    Args:
        lang (str, optional): The language for the vocabulary. Defaults to "es".

    This command calls the manage_vocab function with the IEPNB Keywords vocabulary name,
    the default dataset schema name, and the provided language. The manage_vocab function
    will create the vocabulary and add the IEPNB Keywords to it.

    Returns:
        None
    """
    sdct_cli.manage_vocab(iepnb_config.SCHEMINGDCAT_IEPNB_KEYWORDS_VOCAB, iepnb_config.IEPNB_DEFAULT_DATASET_SCHEMA_NAME, lang)

@iepnb.command()
def delete_iepnb_tags():
    """
    This command deletes the IEPNB Keywords vocabulary.

    This command calls the manage_vocab function with the IEPNB Keywords vocabulary name,
    the default dataset schema name, and the delete flag set to True. The manage_vocab function
    will delete the vocabulary and all its tags.

    Returns:
        None
    """
    sdct_cli.manage_vocab(iepnb_config.SCHEMINGDCAT_IEPNB_KEYWORDS_VOCAB, iepnb_config.IEPNB_DEFAULT_DATASET_SCHEMA_NAME, delete=True)
