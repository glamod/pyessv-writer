#!/bin/bash

# Import utils.
source $PYESSV_WRITER_HOME/sh/utils.sh

# Main entry point.
main()
{
	log "writing GLAMOD vocabs ..."

	declare source=$1

	python $PYESSV_WRITER_HOME/sh/write_glamod_cvs.py --source=$source

	log "GLAMOD cabs written to "$HOME/.esdoc/pyessv-archive
}

# Invoke entry point.
main $1
