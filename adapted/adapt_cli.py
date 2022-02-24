""" Adapt Server

This module contains all the functionality necessary to
setup an Adapt Server node (not really).

Example
-------
    python3 adapt_server.py -v ingest -s testfile.txt
"""

import filesystem
from filesystem import FSOperationError
import sys
import os
import argparse
import logging
from general import hash_entity

from user import User, Keystore
from asset import Asset
from blockchain import BCDB
import config as cfg

logging.basicConfig(format='%(message)s', level=logging.INFO)
LOG = logging.getLogger(__name__)

class AdaptServer():
    """A class to represent an Adapt Server node.

    Attributes
    ----------
    user_list : list
        Holds list of users. (Will probably be removed)

    Methods
    -------
    ingest(file_path, user):
        Ingests a new file (or directory of files) into ADAPT.
    retrieve(tid, user):
        Retrieves a file from ADAPT.
    commit(file_path, prev_tid, user):
        Commits a modified version of a file already existing in ADAPT.
    """
    def initKS(self, num_blocks=5000):
        self.keystore = Keystore()
        self.keystore.save()
        print("keystore init")

    
    def setDebug(self):
        LOG.setLevel(logging.DEBUG)
        filesystem.LOG.setLevel(logging.DEBUG) 

    def __init__(self, bc_address):
        """Constructs all necessary attributes for an AdaptServer object.
        """
        self.user_list = []
        self.keystore = None
        self.fs = filesystem.UpssFs()

        self.bdb = BCDB(bc_address)

    def ingest(self, file_path, user):
        """Ingests a new file (or directory of files) into ADAPT

        Parameters
        ----------
        file_path : str
            Path of file(or directory) to ingest
        user : User
            User performing the ingest

        Returns
        -------
        txid : str
            Transaction id if ingestion is successful
        """
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            sys.exit("File path provided not valid.")

        try:
            self.fs.push(file_path)
        except FSOperationError:
            LOG.error("Ingest operation failed.")
            sys.exit(1)

        fhash = hash_entity(file_path)
        LOG.debug(f"Hash for {file_path}:\n{fhash}\n")

        filename = os.path.basename(file_path)

        data = self.fs.get_data(filename)

        LOG.debug(f"Blockname: {data['bname']}\n")

        A = Asset(
            user.public_key,
            fhash,
            'PUT',
            tags={'ingest'},
            bc_handle=self.bdb
        )
        
        A.push(user.private_key)

        self.keystore.add(A.id, data['bpointer'], filename)
        self.keystore.save()

        return A

    def retrieve(self, tid, user):
        """Retrieves a file from ADAPT

        Parameters
        ----------
        tid : str
            Transaction id of requested file
        user : User
            User performing the retrieval

        Returns
        -------
        txid : str
            Transaction id if retrieval is successfull
        """

        prev_asset = Asset.from_id(tid, self.bdb)
        LOG.debug(f"RETRIEVE:\n{prev_asset}")

        try:
            (bpointer,filename) = self.keystore[tid]
            LOG.debug(f"bpointer: {bpointer}")
        except KeyError:
            LOG.error("Key does not exist in keystore. Exiting now.")
            sys.exit()

        file_path = f"{filesystem.LOC}/{filename}"

        try:
            self.fs.pull(bpointer, file_path)
        except FSOperationError:
            LOG.error("Retrieve operation failed.")
            sys.exit(1)

        LOG.info(f"Copied {filename} from ADAPT-FS to ADAPT workspace")

        local_file_hash = hash_entity(file_path)
        # bc_file_hash = prev_asset.filehash
        # Check if the file has been modified without it being recorded on the blockchain
        # if local_file_hash != bc_file_hash:
        #     LOG.error(f"{file_path} has been modified or tampered with.")

        LOG.debug(f"fhash: {local_file_hash}")

        A = Asset(
            user.public_key,
            local_file_hash,
            'GET',
            parent=prev_asset.id,
            tags={'retrieve'},
            bc_handle=self.bdb
        )
        
        A.push(user.private_key)

        return A

    def commit(self, file_path, prev_tid, user):
        """Commits a modified version of a file already existing in ADAPT

        Parameters
        ----------
        file_path : str
            Path of file to commit
        prev_tid : str
            Transaction id of file prior to modifications
        user : User
            User performing the ingest

        Returns
        -------
        txid : str
            Transaction id if commit is successfull
        """

        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            sys.exit("File path provided not valid.")

        prev_asset = Asset.from_id(prev_tid, self.bdb)

        LOG.debug(f"COMMIT: {prev_asset}")

        try:
            (bpointer,filename) = self.keystore[prev_tid]
            LOG.debug(f"bpointer: {bpointer}")
        except KeyError:
            LOG.error("Key does not exist in keystore. Exiting now.")
            sys.exit()

        try:
            self.fs.push(file_path, filename)
        except FSOperationError:
            LOG.error("Commit operation failed.")
            sys.exit(1)

        try:
            data = self.fs.get_data(filename)
        except FSOperationError:
            LOG.error("Could not find information on given file.")
            sys.exit(1)

        LOG.debug(f"New Blockname: {data['bname']}")

        newfhash = hash_entity(file_path)

        LOG.debug(f"Blockpointer: {data['bpointer']}")

        A = Asset(
            user.public_key,
            newfhash,
            'PUT',
            parent=prev_asset.id,
            tags={'commit'},
            bc_handle=self.bdb
        )
        
        A.push(user.private_key)

        self.keystore.add(A.id, data['bpointer'], filename)
        self.keystore.save()
        
        return A

def main():
    parser = argparse.ArgumentParser(description="Advanced Detection and Prevention of Tampering")
    parser.add_argument('-v', '--verbose', help='increase output verbosity (DEV USE ONLY)', action="store_true")

    subparser = parser.add_subparsers(dest='command')

    ingest = subparser.add_parser('ingest', help="ingest a file into ADAPT")
    retrieve = subparser.add_parser('retrieve', help="retrieve a file from ADAPT")
    commit = subparser.add_parser('commit', help="commit a file into ADAPT")
    init = subparser.add_parser('init', help="initialize ADAPT (only the filesystem)")

    ingest.add_argument('-s', '--source', type=str, required=True, help="stuff")

    retrieve.add_argument('-t', '--tid', type=str, required=True)

    commit.add_argument('-s', '--source', type=str, required=True)
    commit.add_argument('-t', '--tid', type=str, required=True)

    init.add_argument('-n', '--num_blocks', type=int, required=False, default=5000, help="number of blocks")

    args = parser.parse_args()

    user = User("Foobar", "1234")

    node = AdaptServer(cfg.node_addresses['dev'])
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.verbose:
        LOG.setLevel(logging.DEBUG)
        filesystem.LOG.setLevel(logging.DEBUG)

    if args.command == 'init':
        node.keystore = Keystore()
        node.keystore.save()
        try:
            node.fs.initialize(args.num_blocks)
        except FSOperationError:
            LOG.error("Filesystem Initialization Failed.")
            sys.exit(1)
    else:

        node.keystore = Keystore.load()

        if args.command == 'ingest':
            tid = node.ingest(args.source, user)
            LOG.info(f"TID: {tid}")

        elif args.command == 'retrieve':
            tid = node.retrieve(args.tid, user)
            LOG.info(f"TID: {tid}")

        elif args.command == 'commit':
            tid = node.commit(args.source, args.tid, user)
            LOG.info(f"TID: {tid}")

if __name__ == "__main__":
    main()

